"""
CAD Planner
───────────
Converts a natural-language invention idea into a structured CAD specification
using OpenAI GPT-4o-mini (fast, cheap, reliable).

Why OpenAI instead of Gemini?
  The GOOGLE_API_KEY in .env starts with "AQ." which is NOT a valid Gemini key
  (Gemini keys start with "AIza..."). OpenAI key (sk-proj-...) is valid.

Pipeline
────────
User idea (free text)
      │
      ▼
  CADPlanner.build_spec()   ← this file, GPT-4o-mini
      │  extracts:
      │  - component_type   (drone_frame | enclosure | bracket | landing_gear
      │                      | motor_mount | gimbal | payload_bay | propeller_guard)
      │  - span_mm / length_mm / width_mm / height_mm
      │  - wall_mm
      │  - motor_count
      │  - arm_count
      │  - foldable
      │  - has_battery_bay
      │  - material
      │  - extra_features   (list of strings)
      ▼
  Structured CAD spec dict
      │
      ▼
  Parametric generator (generators/parametric_cad.py)
      │  builds real CadQuery geometry from the spec
      ▼
  cq.Workplane  →  GLTF / STEP / STL
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Prompt sent to the LLM
# ─────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a mechanical CAD engineer.
Given a drone / UAV / robotic invention idea, extract a structured JSON spec.

Return ONLY valid JSON — no markdown fences, no explanation.

Schema:
{
  "component_type": one of [
    "drone_frame", "fpv_racing_frame", "enclosure", "bracket",
    "landing_gear", "motor_mount", "gimbal_mount", "payload_bay",
    "propeller_guard", "battery_tray", "vtol_mount"
  ],
  "span_mm": int,          // motor-to-motor or primary span
  "length_mm": int,        // body length
  "width_mm": int,         // body width
  "height_mm": int,        // body / stack height
  "wall_mm": float,        // wall thickness
  "arm_count": int,        // number of arms (3/4/6/8)
  "motor_count": int,      // number of motors
  "foldable": bool,        // foldable arms?
  "has_battery_bay": bool,
  "has_camera_mount": bool,
  "has_prop_guards": bool,
  "material": string,      // e.g. "carbon_fibre", "aluminium", "pla"
  "extra_features": [string] // short list of special features
}

Rules:
- Infer sensible metric dimensions if not stated
- For FPV racing frames, span_mm is typically 150-230
- For freestyle quads, span_mm is 230-280
- For photography drones, span_mm is 350-550
- arm_count must match motor_count
- Always return all fields
"""


class CADPlanner:
    def __init__(self, memory_manager: Any = None):
        self.memory = memory_manager

    # ── Public API ─────────────────────────────────────────────────────────

    async def build_spec(self, idea_text: str) -> dict:
        """Extract structured CAD spec from free-text idea using OpenAI."""
        try:
            return await self._extract_via_openai(idea_text)
        except Exception as exc:
            logger.error("CADPlanner OpenAI extraction failed: %s", exc)
            return self._fallback_spec(idea_text)

    # Keep legacy alias
    async def generate_parameters(self, idea_text: str) -> dict:
        return await self.build_spec(idea_text)

    # ── OpenAI extraction ───────────────────────────────────────────────────

    async def _extract_via_openai(self, idea_text: str) -> dict:
        import httpx, asyncio

        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key or api_key.startswith("sk-your"):
            raise ValueError("No valid OPENAI_API_KEY in environment")

        payload = {
            "model": "gpt-4o-mini",
            "temperature": 0,
            "messages": [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user",   "content": f"Idea: {idea_text}"},
            ],
        }

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}",
                         "Content-Type": "application/json"},
                json=payload,
            )
            resp.raise_for_status()
            raw = resp.json()["choices"][0]["message"]["content"].strip()

        # Strip any accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        spec = json.loads(raw)
        logger.info(
            "CADPlanner spec: type=%s span=%smm motors=%s",
            spec.get("component_type"), spec.get("span_mm"), spec.get("motor_count"),
        )
        return self._normalise(spec)

    # ── Helpers ─────────────────────────────────────────────────────────────

    @staticmethod
    def _normalise(raw: dict) -> dict:
        """Ensure all required keys exist and values are sane."""
        defaults = {
            "component_type":    "drone_frame",
            "span_mm":           300,
            "length_mm":         120,
            "width_mm":          120,
            "height_mm":         20,
            "wall_mm":           3.0,
            "arm_count":         4,
            "motor_count":       4,
            "foldable":          False,
            "has_battery_bay":   True,
            "has_camera_mount":  False,
            "has_prop_guards":   False,
            "material":          "carbon_fibre",
            "extra_features":    [],
        }
        out = {**defaults, **{k: v for k, v in raw.items() if v is not None}}
        # Clamp sanity
        out["span_mm"]   = max(80,  min(2000, int(out["span_mm"])))
        out["length_mm"] = max(40,  min(1000, int(out["length_mm"])))
        out["width_mm"]  = max(40,  min(1000, int(out["width_mm"])))
        out["height_mm"] = max(5,   min(500,  int(out["height_mm"])))
        out["wall_mm"]   = max(1.0, min(10.0, float(out["wall_mm"])))
        out["arm_count"] = max(3,   min(8,    int(out["arm_count"])))
        out["motor_count"] = out["arm_count"]   # keep consistent
        return out

    @staticmethod
    def _fallback_spec(idea_text: str) -> dict:
        """
        Keyword-based fallback when OpenAI is unavailable.
        At least gives a different shape for different ideas.
        """
        text = idea_text.lower()

        if any(w in text for w in ["fpv", "racing", "5 inch", "5inch", "freestyle"]):
            ctype, span = "fpv_racing_frame", 220
        elif any(w in text for w in ["micro", "65mm", "75mm", "tiny"]):
            ctype, span = "fpv_racing_frame", 75
        elif any(w in text for w in ["hexacopter", "hexa", "hex"]):
            ctype, span = "drone_frame", 550
        elif any(w in text for w in ["octocopter", "octo"]):
            ctype, span = "drone_frame", 680
        elif any(w in text for w in ["landing gear", "leg", "skid"]):
            ctype, span = "landing_gear", 400
        elif any(w in text for w in ["enclosure", "box", "case", "housing"]):
            ctype, span = "enclosure", 120
        elif any(w in text for w in ["gimbal", "stabiliz"]):
            ctype, span = "gimbal_mount", 80
        elif any(w in text for w in ["payload", "delivery", "cargo"]):
            ctype, span = "payload_bay", 200
        elif any(w in text for w in ["guard", "protector", "bumper"]):
            ctype, span = "propeller_guard", 250
        else:
            ctype, span = "drone_frame", 450

        # Extract span from text if mentioned explicitly
        import re
        m = re.search(r'(\d{2,4})\s*mm', text)
        if m:
            span = int(m.group(1))

        arm_count  = 6 if "hex" in text else (8 if "octo" in text else 4)
        foldable   = "fold" in text
        cam_mount  = any(w in text for w in ["camera", "fpv", "gopro", "gimbal"])
        prop_guard = "guard" in text

        logger.warning("CADPlanner using keyword fallback for: %.60s", idea_text)
        return {
            "component_type":    ctype,
            "span_mm":           span,
            "length_mm":         max(60, span // 3),
            "width_mm":          max(60, span // 3),
            "height_mm":         20,
            "wall_mm":           2.5,
            "arm_count":         arm_count,
            "motor_count":       arm_count,
            "foldable":          foldable,
            "has_battery_bay":   True,
            "has_camera_mount":  cam_mount,
            "has_prop_guards":   prop_guard,
            "material":          "carbon_fibre",
            "extra_features":    [],
        }
