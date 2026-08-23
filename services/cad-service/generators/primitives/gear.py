"""Landing gear strut primitive."""
import math
import cadquery as cq


def make_landing_strut(
    bx: float, by: float,
    height: float,
    rod_r: float = 4.0,
    foot_r: float = 7.0,
) -> cq.Workplane:
    """Vertical strut + foot pad + diagonal brace to centre."""
    # Vertical rod
    strut = cq.Workplane("XY").center(bx, by).cylinder(height, rod_r)

    # Foot pad (thicker disc at bottom)
    foot = (
        cq.Workplane("XY")
        .center(bx, by)
        .cylinder(rod_r * 0.8, foot_r)
        .translate((0, 0, -height / 2 + rod_r * 0.4))
    )

    # Diagonal brace
    dist  = math.sqrt(bx**2 + by**2)
    angle = math.degrees(math.atan2(by, bx))
    brace = (
        cq.Workplane("XY")
        .transformed(rotate=(0, 0, angle))
        .center(dist / 2, 0)
        .rect(dist, rod_r * 1.2)
        .extrude(rod_r)
        .translate((0, 0, height * 0.4))
    )
    return strut.union(foot).union(brace)
