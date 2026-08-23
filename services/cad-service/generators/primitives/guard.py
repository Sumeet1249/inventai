"""Propeller guard ring primitive."""
import cadquery as cq


def make_prop_ring(
    cx: float, cy: float,
    radius: float,
    thickness: float = 2.5,
    height: float = 3.0,
) -> cq.Workplane:
    """Hollow circular ring for propeller protection."""
    outer = cq.Workplane("XY").center(cx, cy).cylinder(height, radius + thickness)
    inner = cq.Workplane("XY").center(cx, cy).cylinder(height, radius)
    return outer.cut(inner)
