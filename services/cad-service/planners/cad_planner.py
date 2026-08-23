"""
CAD Planner  —  Stage 1 + 2 of the pipeline
─────────────────────────────────────────────
Stage 1: Intent Extraction   (OpenAI gpt-4o-mini)
Stage 2: Requirements JSON   (structured, parameter-classified)

The output feeds into Stage 3 (ConstraintSolver) which resolves
derived/standard values, then Stage 4 (CADSpec) and finally
Stage 5 (ParametricGenerator → cq.Workplane).

Full pipeline:
    User idea
        ↓
    [Stage 1] Intent Extraction          ← OpenAI
        ↓
    [Stage 2] Requirements JSON          ← this file
        ↓
    [Stage 3] Constraint Solver          ← planners/constraint_solver.py
        ↓
    [Stage 4] CAD Spec JSON              ← fully resolved params + provenance
        ↓
    [Stage 5] Parametric Generator       ← generators/parametric_cad.py
        ↓
    cq.Workplane → GLTF / STEP / STL

Why OpenAI and not Gemini?
    GOOGLE_API_KEY in .env starts with "AQ." — not a valid Gemini key.
    OpenAI key (sk-proj-...) is valid and cheap (gpt-4o-mini ~$0.0002/req).
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# ─── OpenAI system prompt ─────────────────────────────────────────────────────

_SYSTEM = """You are a senior mechanical CAD engineer specialising in drones and UAVs.

Given a user's invention idea, extract a structured JSON requirements spec.

Return ONLY valid JSON — no markdown, no explanation.

Schema (all fields required):
{
  "component_type": one of [
    "drone_frame", "fpv_racing_frame", "enclosure", "bracket",
    "landing_gear", "motor_mount", "gimbal_mount", "payload_bay",
    "propeller_guard", "battery_tray", "vtol_mount"
  ],
  "span_mm":        int,     // primary span / motor-to-motor
  "length_mm":      int,     // body length (same as span if symmetric)
  "width_mm":       int,     // body width
  "height_mm":      int,     // body / stack height
  "wall_mm":        float,   // wall thickness
  "arm_count":      int,     // arms (3/4/6/8)
  "motor_count":    int,     // motors (= arm_count)
  "motor_size_mm":  int,     // stator diameter e.g. 2207, 2306
  "foldable":       bool,
  "has_battery_bay":bool,
  "has_camera_mount":bool,
  "has_prop_guards":bool,
  "material":       string,  // "carbon_fibre" | "aluminium" | "pla" | "petg"
  "manufacturing":  string,  // "carbon_fibre" | "fdm" | "cnc" | "sla"
  "extra_features": [string]
}

Engineering rules to follow:
- FPV racing 5-inch → span 210-230mm, arm_count 4
- FPV micro → span 65-100mm
- Photography quad → span 350-550mm
- Hexacopter → arm_count 6
- motor_count must always equal arm_count
- Infer manufacturing from material if not stated
- Be precise with dimensions; prefer round numbers
"""


class CADPlanner:
    def __init__(self, memory_manager: Any = None):
        self.memory = memory_manager

    # ── Public API ─────────────────────────────────────────────────────────

    async def build_spec(self, idea_text: str) -> dict:
        """
        Stage 1+2: Extract requirements from free text.
        Returns raw requirements dict → fed to ConstraintSolver.
        """
        try:
            spec = await self._openai_extract(idea_text)
            logger.info(
                "CADPlanner: type=%s span=%smm arms=%s",
                spec.get("component_type"),
                spec.get("span_mm"),
                spec.get("arm_count"),
            )
            return spec
        except Exception as exc:
            logger.error("CADPlanner OpenAI failed (%s) — using keyword fallback", exc)
            return self._keyword_fallback(idea_text)

    async def generate_parameters(self, idea_text: str) -> dict:
        """Legacy alias."""
        return await self.build_spec(idea_text)

    # ── OpenAI extraction ──────────────────────────────────────────────────

    async def _openai_extract(self, idea: str) -> dict:
        import httpx

        key = os.environ.get("OPENAI_API_KEY", "")
        if not key or key.startswith("sk-your"):
            raise ValueError("No valid OPENAI_API_KEY")

        payload = {
            "model": "gpt-4o-mini",
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": _SYSTEM},
                {"role": "user",   "content": f"Invention idea: {idea}"},
            ],
        }

        async with httpx.AsyncClient(timeout=25) as client:
            r = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}",
                         "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()

        raw = r.json()["choices"][0]["message"]["content"].strip()
        return self._normalise(json.loads(raw))

    # ── Keyword fallback ───────────────────────────────────────────────────

    def _keyword_fallback(self, text: str) -> dict:
        """
        Deterministic keyword-based extractor — always produces a useful spec
        even when OpenAI is unavailable (rate-limit, no key, etc.).
        """
        t = text.lower()

        # Component type detection
        if any(w in t for w in ["fpv", "racing", "freestyle", "5 inch", "5inch", "5\""]):
            ctype, span = "fpv_racing_frame", 220
        elif any(w in t for w in ["micro", "65mm", "75mm", "toothpick", "tiny whoop"]):
            ctype, span = "fpv_racing_frame", 75
        elif any(w in t for w in ["hexacopter", "hex", "hexa", "sextocopter"]):
            ctype, span = "drone_frame", 550
        elif any(w in t for w in ["octocopter", "octo"]):
            ctype, span = "drone_frame", 680
        elif any(w in t for w in ["vtol", "tilt rotor", "tilt-rotor", "hybrid"]):
            ctype, span = "vtol_mount", 350
        elif any(w in t for w in ["landing gear", "landing leg", "skid"]):
            ctype, span = "landing_gear", 400
        elif any(w in t for w in ["enclosure", "box", "case", "housing", "shell"]):
            ctype, span = "enclosure", 120
        elif any(w in t for w in ["gimbal", "stabiliz", "2-axis", "3-axis"]):
            ctype, span = "gimbal_mount", 80
        elif any(w in t for w in ["payload", "delivery", "cargo", "drop"]):
            ctype, span = "payload_bay", 200
        elif any(w in t for w in ["prop guard", "propeller guard", "bumper", "cage"]):
            ctype, span = "propeller_guard", 250
        elif any(w in t for w in ["battery tray", "battery holder", "lipo tray"]):
            ctype, span = "battery_tray", 170
        elif any(w in t for w in ["motor mount", "motor plate"]):
            ctype, span = "motor_mount", 2207
        elif any(w in t for w in ["bracket", "mount", "clamp"]):
            ctype, span = "bracket", 100
        else:
            ctype, span = "drone_frame", 450

        # Span override from explicit mm mention
        m = re.search(r'(\d{2,4})\s*mm', t)
        if m:
            n = int(m.group(1))
            if 50 <= n <= 2000:
                span = n

        # Arm / motor count
        if "hex" in t:   arm_count = 6
        elif "octo" in t: arm_count = 8
        elif "tri" in t:  arm_count = 3
        else:             arm_count = 4

        # Motor size extraction
        motor_m = re.search(r'\b(1\d{3}|2\d{3}|3\d{3}|4\d{3})\b', t)
        motor_sz = int(motor_m.group(1)) if motor_m else 2207

        foldable    = "fold" in t
        cam         = any(w in t for w in ["camera", "fpv", "gopro", "gimbal", "video"])
        guards      = any(w in t for w in ["guard", "cage", "bumper", "protect"])
        battery_bay = not any(w in t for w in ["no battery", "without battery"])

        logger.warning("CADPlanner keyword fallback: type=%s span=%d", ctype, span)

        return self._normalise({
            "component_type":    ctype,
            "span_mm":           span,
            "length_mm":         max(60, span // 3),
            "width_mm":          max(60, span // 3),
            "height_mm":         20,
            "wall_mm":           2.5,
            "arm_count":         arm_count,
            "motor_count":       arm_count,
            "motor_size_mm":     motor_sz,
            "foldable":          foldable,
            "has_battery_bay":   battery_bay,
            "has_camera_mount":  cam,
            "has_prop_guards":   guards,
            "material":          "carbon_fibre",
            "manufacturing":     "carbon_fibre",
            "extra_features":    [],
        })

    # ── Normaliser ─────────────────────────────────────────────────────────

    @staticmethod
    def _normalise(raw: dict) -> dict:
        defaults = {
            "component_type":    "drone_frame",
            "span_mm":           300,
            "length_mm":         120,
            "width_mm":          120,
            "height_mm":         20,
            "wall_mm":           2.5,
            "arm_count":         4,
            "motor_count":       4,
            "motor_size_mm":     2207,
            "foldable":          False,
            "has_battery_bay":   True,
            "has_camera_mount":  False,
            "has_prop_guards":   False,
            "material":          "carbon_fibre",
            "manufacturing":     "carbon_fibre",
            "extra_features":    [],
        }
        out = {**defaults, **{k: v for k, v in raw.items() if v is not None}}
        # Clamp numeric values to sane ranges
        out["span_mm"]      = max(50,  min(2000, int(out["span_mm"])))
        out["length_mm"]    = max(30,  min(1000, int(out["length_mm"])))
        out["width_mm"]     = max(30,  min(1000, int(out["width_mm"])))
        out["height_mm"]    = max(4,   min(500,  int(out["height_mm"])))
        out["wall_mm"]      = max(0.8, min(15.0, float(out["wall_mm"])))
        out["arm_count"]    = max(3,   min(8,    int(out["arm_count"])))
        out["motor_count"]  = out["arm_count"]
        return out
