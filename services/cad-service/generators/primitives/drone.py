"""Drone-frame primitives."""
import math
import cadquery as cq


def make_hub(radius: float, height: float, wall: float) -> cq.Workplane:
    """Hollow cylindrical centre hub."""
    outer = cq.Workplane("XY").cylinder(height, radius)
    inner_r = radius - wall * 2
    if inner_r > 3:
        outer = outer.cut(cq.Workplane("XY").cylinder(height, inner_r))
    return outer


def make_drone_arm(
    length: float,
    width: float,
    height: float,
    angle_deg: float,
    offset_from_centre: float,
) -> cq.Workplane:
    """
    Single arm at a given angle.
    offset_from_centre = hub radius — arm starts here.
    """
    arm = (
        cq.Workplane("XY")
        .transformed(rotate=(0, 0, angle_deg))
        .center(offset_from_centre + length / 2, 0)
        .rect(length, width)
        .extrude(height)
    )
    return arm


def make_motor_pad(
    radius: float,
    height: float,
    cx: float,
    cy: float,
    bolt_circle: float = 16.0,
) -> cq.Workplane:
    """Circular motor mount pad with 4 bolt holes."""
    pad = cq.Workplane("XY").center(cx, cy).cylinder(height, radius)
    # 4 bolt holes on standard pattern
    for i in range(4):
        a  = math.radians(i * 90 + 45)
        bx = cx + math.cos(a) * bolt_circle / 2
        by = cy + math.sin(a) * bolt_circle / 2
        hole = cq.Workplane("XY").center(bx, by).cylinder(height + 2, 1.6)
        pad = pad.cut(hole)
    return pad
