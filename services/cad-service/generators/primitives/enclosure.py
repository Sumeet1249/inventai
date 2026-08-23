"""Electronics enclosure primitives."""
import cadquery as cq


def make_enclosure_shell(L: float, W: float, H: float, wall: float) -> cq.Workplane:
    """Hollow box shell open at top."""
    outer = cq.Workplane("XY").box(L, W, H)
    inner = cq.Workplane("XY").box(
        L - wall * 2, W - wall * 2, H - wall
    ).translate((0, 0, wall / 2))
    return outer.cut(inner)


def make_mounting_boss(
    cx: float, cy: float,
    height: float,
    outer_r: float = 4.0,
    hole_r: float  = 1.6,
    z_offset: float = 0.0,
) -> cq.Workplane:
    """Cylindrical PCB mounting boss with threaded hole."""
    boss = cq.Workplane("XY").center(cx, cy).cylinder(height, outer_r)
    hole = cq.Workplane("XY").center(cx, cy).cylinder(height + 1, hole_r)
    boss = boss.cut(hole)
    return boss.translate((0, 0, z_offset))


def make_usb_cutout(
    width: float = 10.0,
    height: float = 4.0,
    wall_depth: float = 4.0,
    cx: float = 0.0,
    z_center: float = 0.0,
    face: str = "front",   # "front" | "back" | "left" | "right"
) -> cq.Workplane:
    """USB-C / HDMI rectangular port cutout through a wall."""
    cut = (
        cq.Workplane("XZ")
        .center(cx, z_center)
        .rect(width, height)
        .extrude(wall_depth + 2)
    )
    return cut


def make_vent_slots(
    count: int = 5,
    slot_w: float = 3.0,
    slot_h: float = 10.0,
    spacing: float = 6.0,
    depth: float = 5.0,
    cx: float = 0.0,
) -> cq.Workplane:
    """Row of ventilation slots."""
    total_w = count * spacing
    start_x = cx - total_w / 2 + spacing / 2
    slots = cq.Workplane("YZ").center(0, 0).rect(slot_w, slot_h).extrude(depth)
    result = slots.translate((start_x, 0, 0))
    for i in range(1, count):
        s = slots.translate((start_x + i * spacing, 0, 0))
        result = result.union(s)
    return result
