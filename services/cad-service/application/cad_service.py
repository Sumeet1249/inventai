"""
CAD Application Service  v3.0
──────────────────────────────
Full 7-stage pipeline matching the ChatGPT architecture doc:

  Stage 1  Intent Extraction     ← OpenAI gpt-4o-mini
  Stage 2  Requirements JSON     ← CADPlanner
  Stage 3  Constraint Solver     ← ConstraintSolver (deterministic engineering rules)
  Stage 4  CAD Spec JSON         ← fully resolved params + provenance
  Stage 5  Parametric Generator  ← generators/parametric_cad.py (CadQuery)
  Stage 6  Geometry Validation   ← GeometryValidator
  Stage 7  Export GLTF/STEP/STL  ← trimesh + CadQuery exporters

Each stage emits an SSE event so the frontend shows live progress.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import uuid

from fastapi import FastAPI

from packages.ai_core.memory.memory_manager import MemoryManager
from services.cad_service.exporters.gltf_exporter import GLTFExporter
from services.cad_service.exporters.step_exporter import StepExporter
from services.cad_service.exporters.stl_exporter import STLExporter
from services.cad_service.generators.cad_coder_generator import warmup
from services.cad_service.generators.parametric_cad import generate_from_spec
from services.cad_service.planners.cad_planner import CADPlanner
from services.cad_service.planners.constraint_solver import ConstraintSolver
from services.cad_service.schemas.cad_schemas import CADGenerationRequest
from services.cad_service.validators.geometry_validator import GeometryValidator

logger = logging.getLogger(__name__)

EXPORT_DIR = "/tmp/cad_exports"


# ── Application service ────────────────────────────────────────────────────────

class CADApplicationService:
    def __init__(self, memory_manager: MemoryManager):
        self.memory   = memory_manager
        self.planner  = CADPlanner(memory_manager)
        self.solver   = ConstraintSolver()

    async def generate_model_stream(self, request: CADGenerationRequest):
        """
        Yields SSE-formatted data lines for each pipeline stage.
        """
        uid       = str(uuid.uuid4())[:8]
        idea_text = request.effective_prompt or ""
        os.makedirs(EXPORT_DIR, exist_ok=True)

        # ── Stage 1: Intent Extraction ────────────────────────────────────
        yield _sse({"status": "Stage 1 — Extracting design intent…", "stage": 1})

        try:
            requirements = await self.planner.build_spec(idea_text)
        except Exception as exc:
            logger.error("Planner failed: %s", exc)
            requirements = {"component_type": "drone_frame", "span_mm": 300, "arm_count": 4}

        yield _sse({
            "status": f"Stage 2 — Requirements: {requirements.get('component_type')} "
                      f"({requirements.get('span_mm')}mm, {requirements.get('arm_count')} arms)",
            "stage": 2,
            "requirements": {
                k: v for k, v in requirements.items()
                if not k.startswith("_")
            },
        })

        # ── Stage 3: Constraint Solver ────────────────────────────────────
        yield _sse({"status": "Stage 3 — Resolving engineering constraints…", "stage": 3})

        try:
            spec = self.solver.resolve(requirements)
        except Exception as exc:
            logger.error("Constraint solver failed: %s", exc)
            spec = requirements

        provenance = spec.get("_provenance", {})
        explicit   = sum(1 for p in provenance.values() if p.get("source") == "explicit")
        derived    = sum(1 for p in provenance.values() if p.get("source") == "derived")
        assumed    = sum(1 for p in provenance.values()
                        if p.get("source") in ("assumed", "standard"))

        yield _sse({
            "status": f"Stage 4 — CAD Spec ready "
                      f"({explicit} explicit, {derived} derived, {assumed} standard params)",
            "stage": 4,
            "spec_summary": {
                "component_type": spec.get("component_type"),
                "span_mm":        spec.get("span_mm"),
                "arm_count":      spec.get("arm_count"),
                "wall_mm":        spec.get("wall_mm"),
                "material":       spec.get("material", "carbon_fibre"),
            },
            "provenance": provenance,
        })

        # ── Stage 5: Parametric Generator ────────────────────────────────
        yield _sse({"status": "Stage 5 — Building parametric geometry…", "stage": 5})

        loop = asyncio.get_event_loop()
        workplane, gen_code = await loop.run_in_executor(
            None, _run_generation, spec, idea_text
        )

        # ── Stage 6: Geometry Validation ─────────────────────────────────
        yield _sse({"status": "Stage 6 — Validating geometry…", "stage": 6})
        validation_warnings = []
        try:
            GeometryValidator.validate(workplane)
        except Exception as exc:
            validation_warnings.append(str(exc))
            logger.warning("Geometry validation warning: %s", exc)

        # ── Stage 7: Export ───────────────────────────────────────────────
        yield _sse({"status": "Stage 7 — Exporting GLTF / STEP / STL…", "stage": 7})

        step_path = f"{EXPORT_DIR}/model_{uid}.step"
        gltf_path = f"{EXPORT_DIR}/model_{uid}.gltf"
        stl_path  = f"{EXPORT_DIR}/model_{uid}.stl"
        export_errors = []

        try:
            StepExporter.export(workplane, step_path)
        except Exception as exc:
            logger.error("STEP export failed: %s", exc)
            export_errors.append(f"STEP: {exc}")

        try:
            actual = GLTFExporter.export(workplane, gltf_path)
            if actual != gltf_path:
                # Re-export via trimesh to guarantee valid GLTF 2.0
                _retrimesh_gltf(workplane, gltf_path)
        except Exception as exc:
            logger.error("GLTF export failed: %s", exc)
            export_errors.append(f"GLTF: {exc}")

        try:
            STLExporter.export(workplane, stl_path)
        except Exception as exc:
            logger.error("STL export failed: %s", exc)
            export_errors.append(f"STL: {exc}")

        # ── Final payload ─────────────────────────────────────────────────
        final: dict = {
            "id":             uid,
            "status":         "Completed" if not export_errors else "Completed with warnings",
            "stage":          7,
            "parameters":     {k: v for k, v in spec.items() if not k.startswith("_")},
            "provenance":     provenance,
            "generated_code": gen_code,
            "gltf_url":       f"/api/v1/cad/download/model_{uid}.gltf",
            "step_url":       f"/api/v1/cad/download/model_{uid}.step",
            "stl_url":        f"/api/v1/cad/download/model_{uid}.stl",
        }
        if export_errors:      final["warnings"]            = export_errors
        if validation_warnings: final["validation_warnings"] = validation_warnings

        yield _sse(final)
        logger.info("CAD generation complete — id=%s type=%s",
                    uid, spec.get("component_type"))


# ── Helpers ────────────────────────────────────────────────────────────────────

def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def _run_generation(spec: dict, idea_text: str):
    """
    Synchronous worker (runs in executor thread).
    Tries CAD-Coder first (if model loaded), falls back to parametric.
    """
    # Try CAD-Coder if already loaded
    try:
        from services.cad_service.generators.cad_coder_generator import (
            _ModelSingleton, _generate_cadquery_code, _validate_ast, _execute_code
        )
        singleton = _ModelSingleton.get()
        if singleton._loaded:
            code = _generate_cadquery_code(
                spec.get("description", idea_text), spec
            )
            _validate_ast(code)
            wp = _execute_code(code)
            logger.info("CAD-Coder generation succeeded.")
            return wp, code
    except Exception as exc:
        logger.warning("CAD-Coder unavailable, using parametric: %s", exc)

    # Parametric generator — deterministic, idea-specific
    wp   = generate_from_spec(spec)
    code = (
        f"# Parametric generator — {spec.get('component_type')}\n"
        f"# Resolved spec:\n"
        + "\n".join(
            f"#   {k}: {v}"
            for k, v in spec.items()
            if not k.startswith("_") and not isinstance(v, (dict, list))
        )
    )
    return wp, code


def _retrimesh_gltf(workplane, gltf_path: str):
    """Re-export geometry via trimesh to guarantee valid GLTF 2.0."""
    import tempfile, cadquery as _cq, trimesh as _tm
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        tmp = f.name
    try:
        _cq.exporters.export(workplane, tmp)
        mesh = _tm.load(tmp, force="mesh")
        mesh.visual = _tm.visual.ColorVisuals(
            mesh=mesh, vertex_colors=[180, 180, 190, 255])
        gltf_bytes = _tm.exchange.gltf.export_gltf(
            _tm.Scene(geometry={"model": mesh})
        )
        gltf_key = next(
            (k for k in gltf_bytes if k.endswith(".gltf")),
            list(gltf_bytes.keys())[0]
        )
        with open(gltf_path, "wb") as f:
            f.write(gltf_bytes[gltf_key])
        out_dir = os.path.dirname(gltf_path)
        for k, data in gltf_bytes.items():
            if k != gltf_key:
                with open(os.path.join(out_dir, k), "wb") as f:
                    f.write(data)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


# ── FastAPI app ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="InventAI CAD Service",
    description="7-stage AI CAD pipeline: Intent → Requirements → Constraints → Spec → Geometry → Validate → Export",
    version="3.0.0",
)


@app.on_event("startup")
async def _startup():
    """Warm up CAD-Coder model in background (non-blocking)."""
    async def _warmup_task():
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, warmup)
        except Exception as exc:
            logger.warning("CAD-Coder warmup skipped: %s", exc)

    asyncio.ensure_future(_warmup_task())
    logger.info("InventAI CAD Service v3.0 started — 7-stage pipeline active.")


from services.cad_service.api.routers import router  # noqa: E402
app.include_router(router)
