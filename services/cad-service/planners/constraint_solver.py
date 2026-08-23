"""
Constraint Solver
─────────────────
Stage 3 of the CAD pipeline (between Requirements and CAD Spec).

Flow:
  Intent Extraction (OpenAI)
        ↓
  Requirements JSON
        ↓
  ConstraintSolver  ← THIS FILE
        ↓
  CAD Spec JSON  (passed to ParametricGenerator)

Responsibilities:
  1. Classify every parameter as: EXPLICIT | DERIVED | STANDARD | ASSUMED
  2. Resolve derived values using engineering rules (not LLM arithmetic)
  3. Build the final CAD spec with provenance + confidence per parameter
  4. Flag any remaining unknowns

This is deterministic Python — no LLM calls here.
"""

from __future__ import annotations
import logging
import math
from dataclasses import dataclass, field
from typing import Any, Literal

logger = logging.getLogger(__name__)

Source = Literal["explicit", "derived", "standard", "assumed"]

@dataclass
class Param:
    value: Any
    unit: str = "mm"
    source: Source = "assumed"
    confidence: float = 0.80
    reason: str = ""


# ── Engineering standards tables ─────────────────────────────────────────────

# Wall thickness by manufacturing process (mm)
_WALL_BY_PROCESS = {
    "fdm":              2.5,
    "sla":              1.5,
    "cnc":              3.0,
    "sheet_metal":      1.5,
    "injection_mold":   2.0,
    "carbon_fibre":     2.0,
}

# Standard motor mounting patterns (stator_size_mm → bolt_circle_mm)
_MOTOR_BOLT_CIRCLE = {
    1106: 9,  1306: 9,  1404: 12, 1507: 12,
    1804: 12, 2004: 16, 2205: 16, 2207: 16,
    2306: 16, 2312: 19, 2814: 19, 3508: 19,
    4008: 25, 4010: 25, 5010: 25,
}

# Arm width by span (mm span → mm arm width)
def _arm_width(span_mm: int) -> float:
    if span_mm < 120:  return 8.0
    if span_mm < 200:  return 10.0
    if span_mm < 300:  return 12.0
    if span_mm < 450:  return 15.0
    if span_mm < 600:  return 18.0
    return 22.0

# Hub size by arm count
def _hub_radius(span_mm: int, arm_count: int) -> float:
    return max(20.0, span_mm * 0.08 + arm_count * 2)


class ConstraintSolver:
    """
    Takes the raw requirements dict (from CADPlanner.build_spec) and produces
    a fully resolved CAD spec with provenance on every parameter.
    """

    def resolve(self, req: dict) -> dict:
        """
        Main entry point.
        Returns a spec dict ready for ParametricGenerator.generate_from_spec().
        """
        ctype = req.get("component_type", "drone_frame")
        logger.info("ConstraintSolver: resolving %s", ctype)

        resolver = {
            "drone_frame":      self._resolve_drone_frame,
            "fpv_racing_frame": self._resolve_fpv_frame,
            "enclosure":        self._resolve_enclosure,
            "bracket":          self._resolve_bracket,
            "landing_gear":     self._resolve_landing_gear,
            "motor_mount":      self._resolve_motor_mount,
            "gimbal_mount":     self._resolve_gimbal,
            "payload_bay":      self._resolve_payload_bay,
            "propeller_guard":  self._resolve_prop_guard,
            "battery_tray":     self._resolve_battery_tray,
            "vtol_mount":       self._resolve_vtol,
        }.get(ctype, self._resolve_drone_frame)

        params = resolver(req)
        spec   = self._build_spec(ctype, req, params)
        self._log_summary(spec)
        return spec

    # ── Component resolvers ────────────────────────────────────────────────

    def _resolve_drone_frame(self, req: dict) -> dict[str, Param]:
        span       = int(req.get("span_mm", 450))
        arm_count  = int(req.get("arm_count", 4))
        motor_sz   = int(req.get("motor_size_mm", 2207))
        process    = req.get("manufacturing", "carbon_fibre")
        foldable   = bool(req.get("foldable", False))
        has_bay    = bool(req.get("has_battery_bay", True))

        wall = _WALL_BY_PROCESS.get(process, 2.5)
        arm_w   = _arm_width(span)
        hub_r   = _hub_radius(span, arm_count)
        arm_len = span * 0.42
        bolt_c  = _MOTOR_BOLT_CIRCLE.get(motor_sz, 16)

        return {
            "span_mm":         Param(span,      source="explicit" if req.get("span_mm") else "assumed"),
            "arm_count":       Param(arm_count, source="explicit" if req.get("arm_count") else "assumed"),
            "arm_length_mm":   Param(round(arm_len, 1), source="derived",
                                     reason=f"span × 0.42 = {arm_len:.1f}"),
            "arm_width_mm":    Param(arm_w,  source="standard",
                                     reason=f"engineering rule for {span}mm span"),
            "hub_radius_mm":   Param(round(hub_r, 1), source="derived",
                                     reason=f"span×0.08 + arm_count×2 = {hub_r:.1f}"),
            "wall_mm":         Param(wall,   source="standard",
                                     reason=f"{process} standard wall"),
            "height_mm":       Param(max(6, int(span * 0.02)),  source="derived",
                                     reason="span × 0.02"),
            "motor_bolt_circle_mm": Param(bolt_c, source="standard",
                                     reason=f"{motor_sz} motor standard"),
            "foldable":        Param(foldable,  unit="bool", source="explicit" if req.get("foldable") else "assumed"),
            "has_battery_bay": Param(has_bay,   unit="bool", source="explicit" if req.get("has_battery_bay") else "standard"),
            "has_camera_mount":Param(req.get("has_camera_mount", False), unit="bool", source="explicit" if req.get("has_camera_mount") else "assumed"),
        }

    def _resolve_fpv_frame(self, req: dict) -> dict[str, Param]:
        span    = int(req.get("span_mm", 220))
        wall    = _WALL_BY_PROCESS.get("carbon_fibre", 2.0)
        stack_w = 30.5   # Std 30×30 stack
        cam_h   = round(span * 0.15, 1)

        return {
            "span_mm":      Param(span,   source="explicit" if req.get("span_mm") else "assumed"),
            "wall_mm":      Param(wall,   source="standard", reason="carbon fibre FPV standard"),
            "height_mm":    Param(max(4, int(span * 0.028)), source="derived"),
            "plate_length_mm": Param(round(span * 0.55, 1), source="derived", reason="span × 0.55"),
            "plate_width_mm":  Param(round(span * 0.35, 1), source="derived", reason="span × 0.35"),
            "stack_mount_mm":  Param(stack_w, source="standard", reason="30×30 JST stack std"),
            "camera_height_mm":Param(cam_h, source="derived"),
            "has_camera_mount":Param(req.get("has_camera_mount", True), unit="bool",
                                      source="explicit" if req.get("has_camera_mount") else "standard"),
            "has_prop_guards": Param(req.get("has_prop_guards", False), unit="bool",
                                      source="explicit" if req.get("has_prop_guards") else "assumed"),
        }

    def _resolve_enclosure(self, req: dict) -> dict[str, Param]:
        L    = int(req.get("length_mm", 120))
        W    = int(req.get("width_mm", 80))
        H    = int(req.get("height_mm", 40))
        proc = req.get("manufacturing", "fdm")
        wall = _WALL_BY_PROCESS.get(proc, 2.5)

        return {
            "length_mm":   Param(L, source="explicit" if req.get("length_mm") else "assumed"),
            "width_mm":    Param(W, source="explicit" if req.get("width_mm") else "assumed"),
            "height_mm":   Param(H, source="explicit" if req.get("height_mm") else "assumed"),
            "wall_mm":     Param(wall, source="standard", reason=f"{proc} wall standard"),
            "int_length_mm": Param(L - wall*2, source="derived", reason="L - 2×wall"),
            "int_width_mm":  Param(W - wall*2, source="derived", reason="W - 2×wall"),
            "int_height_mm": Param(H - wall,   source="derived", reason="H - wall"),
            "boss_dia_mm": Param(8.0, source="standard", reason="M3 boss standard"),
            "boss_height_mm": Param(H - wall - 1, source="derived"),
            "usb_w_mm":    Param(10.0, source="standard", reason="USB-C cutout std"),
            "usb_h_mm":    Param(4.0,  source="standard"),
            "vent_dia_mm": Param(3.0,  source="standard"),
            "has_camera_mount": Param(req.get("has_camera_mount", False), unit="bool",
                                      source="explicit" if req.get("has_camera_mount") else "assumed"),
        }

    def _resolve_bracket(self, req: dict) -> dict[str, Param]:
        L = int(req.get("length_mm", 100))
        W = int(req.get("width_mm", 50))
        H = int(req.get("height_mm", 40))
        wall = 3.0
        return {
            "length_mm": Param(L, source="explicit" if req.get("length_mm") else "assumed"),
            "width_mm":  Param(W, source="explicit" if req.get("width_mm") else "assumed"),
            "height_mm": Param(H, source="explicit" if req.get("height_mm") else "assumed"),
            "wall_mm":   Param(wall, source="standard"),
            "gusset_h_mm": Param(H * 0.7, source="derived", reason="70% flange height"),
        }

    def _resolve_landing_gear(self, req: dict) -> dict[str, Param]:
        span   = int(req.get("span_mm", 400))
        clear  = int(req.get("height_mm", 80))
        return {
            "span_mm":      Param(span, source="explicit" if req.get("span_mm") else "assumed"),
            "clearance_mm": Param(clear, source="explicit" if req.get("height_mm") else "standard",
                                  reason="80mm ground clearance standard"),
            "rod_radius_mm":Param(4.0, source="standard"),
            "foot_radius_mm":Param(7.0, source="standard"),
            "leg_spread_mm":Param(round(span * 0.38, 1), source="derived", reason="span × 0.38"),
        }

    def _resolve_motor_mount(self, req: dict) -> dict[str, Param]:
        motor_sz  = int(req.get("span_mm", 2207))   # span_mm used as stator mm
        bolt_c    = _MOTOR_BOLT_CIRCLE.get(motor_sz, 16)
        plate_sz  = max(motor_sz * 1.8, 50)
        return {
            "stator_mm":    Param(motor_sz, source="explicit" if req.get("span_mm") else "assumed"),
            "bolt_circle_mm": Param(bolt_c, source="standard",
                                    reason=f"{motor_sz} standard bolt circle"),
            "plate_mm":     Param(round(plate_sz, 1), source="derived"),
            "wall_mm":      Param(3.0, source="standard"),
            "height_mm":    Param(int(req.get("height_mm", 12)), source="explicit" if req.get("height_mm") else "standard"),
        }

    def _resolve_gimbal(self, req: dict) -> dict[str, Param]:
        W = int(req.get("width_mm", 80))
        H = int(req.get("height_mm", 60))
        return {
            "width_mm":  Param(W, source="explicit" if req.get("width_mm") else "assumed"),
            "height_mm": Param(H, source="explicit" if req.get("height_mm") else "assumed"),
            "wall_mm":   Param(2.5, source="standard"),
            "roll_radius_mm": Param(round(H * 0.45, 1), source="derived"),
            "post_height_mm": Param(round(H * 0.25, 1), source="derived"),
        }

    def _resolve_payload_bay(self, req: dict) -> dict[str, Param]:
        L = int(req.get("length_mm", 150))
        W = int(req.get("width_mm", 100))
        H = int(req.get("height_mm", 80))
        wall = 2.5
        return {
            "length_mm": Param(L, source="explicit" if req.get("length_mm") else "assumed"),
            "width_mm":  Param(W, source="explicit" if req.get("width_mm") else "assumed"),
            "height_mm": Param(H, source="explicit" if req.get("height_mm") else "assumed"),
            "wall_mm":   Param(wall, source="standard"),
            "hatch_length_mm": Param(L - wall*4, source="derived"),
            "hatch_width_mm":  Param(W - wall*4, source="derived"),
        }

    def _resolve_prop_guard(self, req: dict) -> dict[str, Param]:
        span      = int(req.get("span_mm", 250))
        arm_count = int(req.get("arm_count", 4))
        prop_r    = round(span / 4 * 0.55, 1)
        hub_r     = max(20, round(span * 0.08, 1))
        arm_len   = round(span / 2 - hub_r - prop_r, 1)
        return {
            "span_mm":     Param(span, source="explicit" if req.get("span_mm") else "assumed"),
            "arm_count":   Param(arm_count, source="explicit" if req.get("arm_count") else "assumed"),
            "prop_radius_mm": Param(prop_r, source="derived", reason="span/4 × 0.55"),
            "hub_radius_mm":  Param(hub_r,  source="derived"),
            "arm_length_mm":  Param(max(5, arm_len), source="derived"),
            "ring_thickness_mm": Param(2.5, source="standard"),
        }

    def _resolve_battery_tray(self, req: dict) -> dict[str, Param]:
        L = int(req.get("length_mm", 170))
        W = int(req.get("width_mm", 47))
        H = int(req.get("height_mm", 36))
        wall = 2.0
        return {
            "length_mm": Param(L, source="explicit" if req.get("length_mm") else "assumed"),
            "width_mm":  Param(W, source="explicit" if req.get("width_mm") else "assumed"),
            "height_mm": Param(H, source="explicit" if req.get("height_mm") else "assumed"),
            "wall_mm":   Param(wall, source="standard"),
            "strap_slot_w_mm": Param(12.0, source="standard", reason="20mm velcro strap"),
        }

    def _resolve_vtol(self, req: dict) -> dict[str, Param]:
        span = int(req.get("span_mm", 300))
        wall = 3.0
        return {
            "span_mm":    Param(span, source="explicit" if req.get("span_mm") else "assumed"),
            "wall_mm":    Param(wall, source="standard"),
            "height_mm":  Param(int(req.get("height_mm", 20)), source="explicit" if req.get("height_mm") else "standard"),
            "arm_length_mm": Param(round(span * 0.45, 1), source="derived"),
            "pivot_radius_mm": Param(round(span * 0.03, 1), source="derived"),
        }

    # ── Build final spec ───────────────────────────────────────────────────

    def _build_spec(self, ctype: str, req: dict, params: dict[str, Param]) -> dict:
        """
        Merge resolved params back into the flat spec dict that
        ParametricGenerator.generate_from_spec() expects, plus attach
        a provenance block for UI display.
        """
        flat = {k: p.value for k, p in params.items()}
        flat["component_type"] = ctype

        # Copy non-geometric flags from req
        for key in ("has_battery_bay", "has_camera_mount", "has_prop_guards",
                    "foldable", "material", "extra_features"):
            if key in req and key not in flat:
                flat[key] = req[key]

        # Provenance block — shown in frontend assumptions panel
        flat["_provenance"] = {
            k: {
                "value":      p.value,
                "unit":       p.unit,
                "source":     p.source,
                "confidence": p.confidence,
                "reason":     p.reason,
            }
            for k, p in params.items()
        }
        return flat

    def _log_summary(self, spec: dict):
        prov = spec.get("_provenance", {})
        explicit = sum(1 for p in prov.values() if p["source"] == "explicit")
        derived  = sum(1 for p in prov.values() if p["source"] == "derived")
        assumed  = sum(1 for p in prov.values() if p["source"] in ("assumed", "standard"))
        logger.info(
            "Constraint resolved: %d explicit, %d derived, %d standard/assumed",
            explicit, derived, assumed
        )
