"""
CAD Primitives Library
───────────────────────
Reusable CadQuery building blocks composed by the parametric generator.

Usage:
    from services.cad_service.generators.primitives import (
        make_drone_arm, make_motor_pad, make_hub,
        make_enclosure_shell, make_mounting_boss,
        make_usb_cutout, make_vent_slots,
        make_prop_ring, make_landing_strut,
    )
"""
from .drone     import make_drone_arm, make_motor_pad, make_hub
from .enclosure import make_enclosure_shell, make_mounting_boss, make_usb_cutout, make_vent_slots
from .guard     import make_prop_ring
from .gear      import make_landing_strut

__all__ = [
    "make_drone_arm", "make_motor_pad", "make_hub",
    "make_enclosure_shell", "make_mounting_boss", "make_usb_cutout", "make_vent_slots",
    "make_prop_ring", "make_landing_strut",
]
