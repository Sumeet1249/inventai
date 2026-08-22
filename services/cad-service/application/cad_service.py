"""
CAD Application Service
───────────────────────
FastAPI app + business-logic orchestrator for the InventAI CAD pipeline.

New pipeline (replaces the old hardcoded generate_drone approach):

  POST /api/v1/cad/generate
        │
        ▼
  1. CADPlanner.build_spec()          — Gemini 1.5 Flash → structured spec
        │
        ▼
  2. generate_with_cad_coder()        — CAD-Coder 7B (4-bit NF4) → CadQuery code
        │
        ▼
  3. GeometryValidator.validate()     — volume + bounding-box sanity check
        │
        ▼
  4. Exporters                        — STEP / STL / GLTF via trimesh
        │
        ▼
  SSE stream → frontend ThreeViewer
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
from services.cad_service.generators.cad_coder_generator import (
    generate_with_cad_coder,
    warmup,
)
from services.cad_service.planners.cad_planner import CADPlanner
from services.cad_service.schemas.cad_schemas import (
    CADGenerationRequest,
    CADModelResponse,
)
from services.cad_service.validators.geometry_validator import GeometryValidator

logger = logging.getLogger(__name__)

EXPORT_DIR = "/tmp/cad_exports"


# ── Application service ───────────────────────────────────────────────────────

class CADApplicationService:
    """
    Business-logic orchestrator.
    Yields Server-Sent Events so the frontend can show live progress.
    """

    def __init__(self, memory_manager: MemoryManager):
        self.memory  = memory_manager
        self.planner = CADPlanner(memory_manager)

    async def generate_model_stream(self, request: CADGenerationRequest):
        """
        Async generator that yields SSE-formatted data lines.

        Every yield looks like:
            data: {"status": "...", ...optional fields...}\n\n

        The final event also carries:
            id, parameters, gltf_url, step_url, stl_url, generated_code
        """
        unique_id   = str(uuid.uuid4())[:8]
        idea_text   = request.effective_prompt or ""
        os.makedirs(EXPORT_DIR, exist_ok=True)

        # ── Stage 1: Planning (Gemini → structured spec) ──────────────────
        yield _sse({"status": "Analyzing idea with Gemini…"})
        try:
            spec = await self.planner.build_spec(idea_text)
        except Exception as exc:
            logger.error("Planner failed: %s", exc)
            spec = {
                "description": idea_text,
                "component":   "mechanical part",
                "material":    "aluminum",
                "span_mm":     200,
                "height_mm":   20,
                "width_mm":    200,
                "motor_count": 0,
            }

        yield _sse({
            "status": f"Spec ready — generating {spec.get('component_type', 'part')} "
                      f"({spec.get('span_mm', '?')} mm) with parametric CAD engine…"
        })

        # ── Stage 2: Parametric CAD generation (uses spec directly) ───────
        yield _sse({"status": "Building parametric geometry…"})

        from services.cad_service.generators.parametric_cad import generate_from_spec

        loop = asyncio.get_event_loop()
        workplane, generated_code = await loop.run_in_executor(
            None,
            _run_generation,
            spec,
            idea_text,
        )

        yield _sse({"status": "CAD-Coder: code generated, validating geometry…"})

        # ── Stage 3: Geometry validation ──────────────────────────────────
        try:
            GeometryValidator.validate(workplane)
        except Exception as exc:
            logger.warning("Geometry validation warning: %s", exc)
            yield _sse({"status": f"Validation warning: {exc} — continuing…"})

        # ── Stage 4: Export STEP / STL / GLTF ────────────────────────────
        yield _sse({"status": "Exporting STEP / STL / GLTF…"})

        step_path = f"{EXPORT_DIR}/model_{unique_id}.step"
        gltf_path = f"{EXPORT_DIR}/model_{unique_id}.gltf"
        stl_path  = f"{EXPORT_DIR}/model_{unique_id}.stl"

        export_errors: list[str] = []

        try:
            StepExporter.export(workplane, step_path)
        except Exception as exc:
            logger.error("STEP export failed: %s", exc)
            export_errors.append(f"STEP: {exc}")

        try:
            actual_gltf = GLTFExporter.export(workplane, gltf_path)
            if actual_gltf != gltf_path:
                try:
                    import trimesh, tempfile, os as _os
                    import cadquery as _cq
                    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
                        stl_tmp = tmp.name
                    _cq.exporters.export(workplane, stl_tmp)
                    mesh = trimesh.load(stl_tmp, force="mesh")
                    mesh.visual = trimesh.visual.ColorVisuals(
                        mesh=mesh, vertex_colors=[180, 180, 190, 255])
                    scene = trimesh.Scene(geometry={"model": mesh})
                    gltf_bytes = trimesh.exchange.gltf.export_gltf(scene)
                    gltf_key = next(
                        (k for k in gltf_bytes if k.endswith(".gltf")),
                        list(gltf_bytes.keys())[0])
                    with open(gltf_path, "wb") as f:
                        f.write(gltf_bytes[gltf_key])
                    out_dir = _os.path.dirname(gltf_path)
                    for key, data in gltf_bytes.items():
                        if key == gltf_key:
                            continue
                        with open(_os.path.join(out_dir, key), "wb") as f:
                            f.write(data)
                    if _os.path.exists(stl_tmp):
                        _os.unlink(stl_tmp)
                    logger.info("GLTF re-exported successfully after fallback.")
                except Exception as retry_exc:
                    logger.error("GLTF retry also failed: %s", retry_exc)
                    export_errors.append(f"GLTF retry: {retry_exc}")
        except Exception as exc:
            logger.error("GLTF export failed: %s", exc)
            export_errors.append(f"GLTF: {exc}")
            actual_gltf = gltf_path

        try:
            STLExporter.export(workplane, stl_path)
        except Exception as exc:
            logger.error("STL export failed: %s", exc)
            export_errors.append(f"STL: {exc}")

        # ── Stage 5: Final SSE payload ────────────────────────────────────
        yield _sse({"status": "Uploading artifacts…"})
        await asyncio.sleep(0.2)

        final: dict = {
            "id":             unique_id,
            "status":         "Completed" if not export_errors else "Completed with warnings",
            "parameters":     spec,
            "generated_code": generated_code,          # shown in frontend debug panel
            "gltf_url":       f"/api/v1/cad/download/model_{unique_id}.gltf",
            "step_url":       f"/api/v1/cad/download/model_{unique_id}.step",
            "stl_url":        f"/api/v1/cad/download/model_{unique_id}.stl",
        }
        if export_errors:
            final["warnings"] = export_errors

        yield _sse(final)
        logger.info("CAD generation complete: id=%s", unique_id)


# ── Helper ────────────────────────────────────────────────────────────────────

def _sse(payload: dict) -> str:
    """Format a dict as a Server-Sent Event data line."""
    return f"data: {json.dumps(payload)}\n\n"


def _run_generation(spec: dict, idea_text: str):
    """
    Synchronous worker executed in a thread.
    Tries CAD-Coder (if model is loaded), falls back to parametric generator.
    Returns (cq.Workplane, code_str).
    """
    from services.cad_service.generators.parametric_cad import generate_from_spec

    # Try CAD-Coder first (only if model already loaded — don't block)
    try:
        from services.cad_service.generators.cad_coder_generator import (
            _ModelSingleton, _generate_cadquery_code, _validate_ast, _execute_code
        )
        singleton = _ModelSingleton.get()
        if singleton._loaded:
            code = _generate_cadquery_code(spec.get("description", idea_text), spec)
            _validate_ast(code)
            wp = _execute_code(code)
            logger.info("CAD-Coder generation succeeded.")
            return wp, code
    except Exception as exc:
        logger.warning("CAD-Coder not available, using parametric generator: %s", exc)

    # Parametric generator — always works, idea-specific shapes
    wp = generate_from_spec(spec)
    code = f"# Parametric generator: {spec.get('component_type', 'drone_frame')}\n# spec: {json.dumps(spec, indent=2)}"
    return wp, code


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="InventAI CAD Service",
    description="Text-to-3D CAD generation — CAD-Coder + CadQuery + trimesh",
    version="2.0.0",
)


@app.on_event("startup")
async def _startup():
    """
    Warm up CAD-Coder in a background thread at service start.
    The model (~4.5 GB 4-bit) is downloaded once to /models/hf_cache
    (Docker volume) and reused on subsequent restarts.
    Warmup failure is logged but NEVER crashes the server — the model
    will be loaded lazily on the first actual /cad/generate request.
    """
    import asyncio

    async def _warmup_task():
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, warmup)
        except Exception as exc:
            # Intentionally swallow — model loads lazily on first request
            logger.warning("CAD-Coder startup warmup skipped: %s", exc)

    # Fire and forget — don't await, never block startup
    asyncio.ensure_future(_warmup_task())
    logger.info("CAD service v2.0 started — CAD-Coder will load on first request.")


# Lazy import to avoid circular dependencies at module load time
from services.cad_service.api.routers import router  # noqa: E402
app.include_router(router)
