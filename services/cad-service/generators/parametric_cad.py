"""
Parametric CAD Generator
────────────────────────
Converts a structured CAD spec (from CADPlanner) into a real cq.Workplane
geometry. Each component_type produces a visually distinct 3-D shape.

No LLM involved here — pure deterministic CadQuery geometry.
"""

from __future__ import annotations

import logging
import math
import cadquery as cq

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────────────

def generate_from_spec(spec: dict) -> cq.Workplane:
    """
    Dispatch to the right generator based on spec['component_type'].
    Falls back to a generic drone frame on unknown types.
    """
    ctype = spec.get("component_type", "drone_frame")
    logger.info("Parametric generator: type=%s span=%s", ctype, spec.get("span_mm"))

    generators = {
        "drone_frame":      _drone_frame,
        "fpv_racing_frame": _fpv_racing_frame,
        "enclosure":        _electronics_enclosure,
        "bracket":          _mounting_bracket,
        "landing_gear":     _landing_gear,
        "motor_mount":      _motor_mount,
        "gimbal_mount":     _gimbal_mount,
        "payload_bay":      _payload_bay,
        "propeller_guard":  _propeller_guard,
        "battery_tray":     _battery_tray,
        "vtol_mount":       _vtol_mount,
    }

    fn = generators.get(ctype, _drone_frame)
    try:
        result = fn(spec)
        logger.info("Parametric generation complete: %s", ctype)
        return result
    except Exception as exc:
        logger.error("Parametric generator failed for %s: %s — using fallback", ctype, exc, exc_info=True)
        return _safe_fallback(spec)


# ──────────────────────────────────────────────────────────────────────────────
# 1. Standard drone frame  (quad / hex / octo)
# ──────────────────────────────────────────────────────────────────────────────

def _drone_frame(spec: dict) -> cq.Workplane:
    span       = spec.get("span_mm", 450)
    arm_count  = int(spec.get("arm_count", 4))
    wall       = spec.get("wall_mm", 3.0)
    h          = spec.get("height_mm", 8)
    foldable   = spec.get("foldable", False)
    has_bay    = spec.get("has_battery_bay", True)

    arm_len    = span * 0.42
    arm_w      = max(12, span * 0.045)
    hub_r      = max(30, span * 0.13)
    hub_h      = h * 1.4

    # Central hub
    frame = (
        cq.Workplane("XY")
        .cylinder(hub_h, hub_r)
    )

    # Hollow centre
    cutout_r = hub_r - wall * 2
    if cutout_r > 5:
        frame = frame.cut(
            cq.Workplane("XY").cylinder(hub_h, cutout_r)
        )

    # Arms
    angle_step = 360.0 / arm_count
    for i in range(arm_count):
        angle_rad = math.radians(i * angle_step)
        cx = math.cos(angle_rad) * (hub_r + arm_len / 2)
        cy = math.sin(angle_rad) * (hub_r + arm_len / 2)

        arm = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, math.degrees(angle_rad)))
            .center(hub_r + arm_len / 2, 0)
            .rect(arm_len, arm_w)
            .extrude(h)
        )
        frame = frame.union(arm)

        # Motor mount pad at arm tip
        mx = math.cos(angle_rad) * (hub_r + arm_len)
        my = math.sin(angle_rad) * (hub_r + arm_len)
        mount_r = arm_w * 0.7
        mount = (
            cq.Workplane("XY")
            .center(mx, my)
            .cylinder(h * 1.6, mount_r)
        )
        frame = frame.union(mount)

    # Battery bay on top
    if has_bay:
        bay_l = hub_r * 1.6
        bay_w = hub_r * 0.9
        bay_h = h * 0.8
        bay = (
            cq.Workplane("XY")
            .center(0, 0)
            .rect(bay_l, bay_w)
            .extrude(hub_h + bay_h)
        )
        # hollow it
        inner = (
            cq.Workplane("XY")
            .center(0, 0)
            .rect(bay_l - wall * 2, bay_w - wall * 2)
            .extrude(hub_h + bay_h + 1)
        )
        bay = bay.cut(inner)
        frame = frame.union(bay)

    # Foldable hinges (visual only)
    if foldable:
        for i in range(arm_count):
            angle_rad = math.radians(i * angle_step)
            hx = math.cos(angle_rad) * (hub_r + arm_w)
            hy = math.sin(angle_rad) * (hub_r + arm_w)
            hinge = (
                cq.Workplane("XY")
                .center(hx, hy)
                .cylinder(h * 2.5, arm_w * 0.4)
            )
            frame = frame.union(hinge)

    return frame


# ──────────────────────────────────────────────────────────────────────────────
# 2. FPV racing frame  (stretched-X / true-X)
# ──────────────────────────────────────────────────────────────────────────────

def _fpv_racing_frame(spec: dict) -> cq.Workplane:
    span    = spec.get("span_mm", 220)
    wall    = spec.get("wall_mm", 2.5)
    h       = max(4, spec.get("height_mm", 6))
    cam     = spec.get("has_camera_mount", True)
    guards  = spec.get("has_prop_guards", False)

    # Main plate — stretched-X shape
    plate_l  = span * 0.55
    plate_w  = span * 0.35
    arm_len  = span * 0.48
    arm_w    = max(10, span * 0.06)
    motor_r  = arm_w * 0.75

    # Bottom plate
    frame = (
        cq.Workplane("XY")
        .rect(plate_l, plate_w)
        .extrude(h)
    )

    # 4 arms at ±30° front, ±20° rear (typical racing geometry)
    arm_angles = [30, -30, 160, -160]
    for angle in arm_angles:
        a = math.radians(angle)
        cx = math.cos(a) * (plate_l / 2 + arm_len / 2)
        cy = math.sin(a) * (plate_w / 2 + arm_len / 2)
        arm = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle))
            .center(plate_l / 2 + arm_len / 2, 0)
            .rect(arm_len, arm_w)
            .extrude(h)
        )
        frame = frame.union(arm)
        mx = math.cos(a) * (plate_l / 2 + arm_len)
        my = math.sin(a) * (plate_w / 2 + arm_len)
        mount = cq.Workplane("XY").center(mx, my).cylinder(h * 1.8, motor_r)
        frame = frame.union(mount)

    # Top plate (standoffs implied by height)
    top = (
        cq.Workplane("XY")
        .center(0, 0)
        .rect(plate_l * 0.8, plate_w * 0.8)
        .extrude(h * 0.4)
        .translate((0, 0, h * 2))
    )
    frame = frame.union(top)

    # Camera mount at front
    if cam:
        cam_w = max(20, span * 0.12)
        cam_h = span * 0.15
        cam_t = wall
        cam_mount = (
            cq.Workplane("XY")
            .center(plate_l / 2 + cam_w / 2, 0)
            .rect(cam_t, cam_w)
            .extrude(cam_h)
            .translate((0, 0, h))
        )
        frame = frame.union(cam_mount)

    # Prop guards (rings)
    if guards:
        for angle in arm_angles:
            a   = math.radians(angle)
            mx  = math.cos(a) * (plate_l / 2 + arm_len)
            my  = math.sin(a) * (plate_w / 2 + arm_len)
            pr  = span / 4 * 0.55
            ring_outer = cq.Workplane("XY").center(mx, my).cylinder(3, pr)
            ring_inner = cq.Workplane("XY").center(mx, my).cylinder(3, pr - 2)
            frame = frame.union(ring_outer.cut(ring_inner).translate((0, 0, h / 2)))

    return frame


# ──────────────────────────────────────────────────────────────────────────────
# 3. Electronics enclosure
# ──────────────────────────────────────────────────────────────────────────────

def _electronics_enclosure(spec: dict) -> cq.Workplane:
    L    = spec.get("length_mm", 120)
    W    = spec.get("width_mm",  80)
    H    = spec.get("height_mm", 40)
    wall = spec.get("wall_mm", 2.5)
    cam  = spec.get("has_camera_mount", False)

    # Outer shell
    box = cq.Workplane("XY").box(L, W, H)

    # Hollow interior
    inner = cq.Workplane("XY").box(L - wall*2, W - wall*2, H - wall)
    inner = inner.translate((0, 0, wall / 2))
    box = box.cut(inner)

    # 4 mounting bosses in corners
    boss_r    = 4
    boss_h    = H - wall
    offsets   = [(L/2 - 8, W/2 - 8), (-(L/2 - 8), W/2 - 8),
                 (L/2 - 8, -(W/2 - 8)), (-(L/2 - 8), -(W/2 - 8))]
    for (ox, oy) in offsets:
        boss = (
            cq.Workplane("XY")
            .center(ox, oy)
            .cylinder(boss_h, boss_r)
            .translate((0, 0, wall / 2 - H / 2))
        )
        box = box.union(boss)

    # USB-C cutout on front face
    usb_w, usb_h = 10, 4
    usb_cut = (
        cq.Workplane("XZ")
        .center(0, -H/2 + wall + usb_h/2 + 4)
        .rect(usb_w, usb_h)
        .extrude(wall + 2)
        .translate((0, W/2 - wall/2, 0))
    )
    box = box.cut(usb_cut)

    # Ventilation slots on sides
    slot_w, slot_h = 3, 10
    for i in range(-2, 3):
        slot = (
            cq.Workplane("YZ")
            .center(0, 0)
            .rect(slot_w, slot_h)
            .extrude(wall + 2)
            .translate((L/2 - wall/2, i * 12, 0))
        )
        box = box.cut(slot)

    # Camera mount bracket on top
    if cam:
        brkt = (
            cq.Workplane("XY")
            .center(0, -W/2 - 8)
            .rect(30, 16)
            .extrude(H / 2)
            .translate((0, 0, H / 4))
        )
        box = box.union(brkt)

    return box


# ──────────────────────────────────────────────────────────────────────────────
# 4. Mounting bracket
# ──────────────────────────────────────────────────────────────────────────────

def _mounting_bracket(spec: dict) -> cq.Workplane:
    L    = spec.get("length_mm", 100)
    W    = spec.get("width_mm", 50)
    H    = spec.get("height_mm", 10)
    wall = spec.get("wall_mm", 3.0)

    base = cq.Workplane("XY").box(L, W, wall)

    # Vertical flange
    flange = (
        cq.Workplane("XZ")
        .center(0, wall / 2)
        .rect(L, H)
        .extrude(wall)
        .translate((0, -W/2 + wall/2, H/2))
    )
    bracket = base.union(flange)

    # Mounting holes on base (4×)
    for (ox, oy) in [(L/2-10, W/2-10), (-(L/2-10), W/2-10),
                     (L/2-10, -(W/2-10)), (-(L/2-10), -(W/2-10))]:
        hole = cq.Workplane("XY").center(ox, oy).cylinder(wall + 2, 3.2)
        bracket = bracket.cut(hole)

    # Slots on flange
    for ox in [-L/4, 0, L/4]:
        slot = (
            cq.Workplane("XZ")
            .center(ox, H/4 + wall/2)
            .rect(6, H/2)
            .extrude(wall + 2)
            .translate((0, -W/2, H/4))
        )
        bracket = bracket.cut(slot)

    # Gusset triangles
    for sx in [-1, 1]:
        tri = (
            cq.Workplane("XZ")
            .polyline([(0,0),(W*0.4,0),(0,H*0.7),(0,0)])
            .close()
            .extrude(wall)
            .translate((sx*(L/2 - wall*2), -W/2 + wall, 0))
        )
        bracket = bracket.union(tri)

    return bracket


# ──────────────────────────────────────────────────────────────────────────────
# 5. Landing gear
# ──────────────────────────────────────────────────────────────────────────────

def _landing_gear(spec: dict) -> cq.Workplane:
    span      = spec.get("span_mm", 400)
    clearance = spec.get("height_mm", 80)
    rod_r     = 4
    foot_r    = 7
    count     = 4

    gear = cq.Workplane("XY").box(1, 1, 1)   # dummy start
    first = True

    for i in range(count):
        angle = math.radians(i * 90)
        bx    = math.cos(angle) * span * 0.38
        by    = math.sin(angle) * span * 0.38

        # Vertical strut
        strut = (
            cq.Workplane("XY")
            .center(bx, by)
            .cylinder(clearance, rod_r)
        )
        # Foot pad
        foot = (
            cq.Workplane("XY")
            .center(bx, by)
            .cylinder(rod_r * 0.8, foot_r)
            .translate((0, 0, -clearance/2 + rod_r * 0.4))
        )
        # Diagonal brace to centre
        brace_len = math.sqrt(bx**2 + by**2)
        brace = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, math.degrees(angle)))
            .center(bx / 2, 0)
            .rect(brace_len, rod_r * 1.2)
            .extrude(rod_r)
            .translate((0, 0, clearance * 0.4))
        )
        leg = strut.union(foot).union(brace)
        if first:
            gear = leg
            first = False
        else:
            gear = gear.union(leg)

    # Top mounting plate
    plate = (
        cq.Workplane("XY")
        .rect(span * 0.25, span * 0.25)
        .extrude(rod_r)
        .translate((0, 0, clearance / 2))
    )
    gear = gear.union(plate)
    return gear


# ──────────────────────────────────────────────────────────────────────────────
# 6. Motor mount
# ──────────────────────────────────────────────────────────────────────────────

def _motor_mount(spec: dict) -> cq.Workplane:
    span   = spec.get("span_mm", 30)   # motor stator diameter
    wall   = spec.get("wall_mm", 3.0)
    H      = spec.get("height_mm", 12)
    plate  = max(span * 1.8, 50)

    base = cq.Workplane("XY").box(plate, plate, wall)

    # Circular motor boss
    boss = cq.Workplane("XY").cylinder(H, span / 2 + wall)
    shaft_hole = cq.Workplane("XY").cylinder(H + 2, span / 2 - wall)
    boss = boss.cut(shaft_hole)
    mount = base.union(boss)

    # 4 screw holes on motor pattern (16mm standard)
    bolt_circle = span * 0.55
    for i in range(4):
        a   = math.radians(i * 90 + 45)
        bx  = math.cos(a) * bolt_circle
        by  = math.sin(a) * bolt_circle
        hole = cq.Workplane("XY").center(bx, by).cylinder(H + 4, 1.5)
        mount = mount.cut(hole)

    # Corner mounting holes
    for (ox, oy) in [(plate/2-6, plate/2-6), (-plate/2+6, plate/2-6),
                     (plate/2-6, -plate/2+6), (-plate/2+6, -plate/2+6)]:
        h = cq.Workplane("XY").center(ox, oy).cylinder(wall + 2, 2.5)
        mount = mount.cut(h)

    return mount


# ──────────────────────────────────────────────────────────────────────────────
# 7. Gimbal mount
# ──────────────────────────────────────────────────────────────────────────────

def _gimbal_mount(spec: dict) -> cq.Workplane:
    W    = spec.get("width_mm", 80)
    H    = spec.get("height_mm", 60)
    wall = spec.get("wall_mm", 2.5)

    # Base plate
    base = cq.Workplane("XY").box(W, W * 0.7, wall)

    # Vibration isolation posts (4×)
    post_h = H * 0.25
    for (ox, oy) in [(W/2-8, W*0.3), (-W/2+8, W*0.3),
                     (W/2-8, -W*0.3+5), (-W/2+8, -W*0.3+5)]:
        post = cq.Workplane("XY").center(ox, oy).cylinder(post_h, 4)
        base = base.union(post)
        ball = cq.Workplane("XY").center(ox, oy).sphere(5).translate((0,0,post_h+wall/2))
        base = base.union(ball)

    # Roll axis frame
    roll_r  = H * 0.45
    roll_ring = (
        cq.Workplane("XY")
        .cylinder(wall * 1.5, roll_r)
        .cut(cq.Workplane("XY").cylinder(wall * 1.5, roll_r - wall * 2))
        .translate((0, 0, post_h + 10))
    )
    base = base.union(roll_ring)

    # Camera tray inside roll frame
    tray = (
        cq.Workplane("XY")
        .box(W * 0.5, H * 0.3, wall)
        .translate((0, 0, post_h + 10))
    )
    base = base.union(tray)
    return base


# ──────────────────────────────────────────────────────────────────────────────
# 8. Payload bay
# ──────────────────────────────────────────────────────────────────────────────

def _payload_bay(spec: dict) -> cq.Workplane:
    L    = spec.get("length_mm", 150)
    W    = spec.get("width_mm", 100)
    H    = spec.get("height_mm", 80)
    wall = spec.get("wall_mm", 2.5)

    # Shell
    box = cq.Workplane("XY").box(L, W, H)
    inner = cq.Workplane("XY").box(L - wall*2, W - wall*2, H - wall).translate((0, 0, wall/2))
    box = box.cut(inner)

    # Bottom hatch (removable panel implied by cutout)
    hatch_w = W - wall * 4
    hatch_l = L - wall * 4
    hatch   = (
        cq.Workplane("XY")
        .center(0, 0)
        .rect(hatch_l, hatch_w)
        .extrude(wall + 1)
        .translate((0, 0, -H/2 - 0.5))
    )
    box = box.cut(hatch)

    # Servo mount tabs on bottom
    for sx in [-1, 1]:
        tab = (
            cq.Workplane("XY")
            .center(sx * (L/2 + 6), 0)
            .box(12, 20, wall * 2)
        )
        box = box.union(tab)

    # Suspension mounts on top
    for (ox, oy) in [(L/2-12, 0), (-L/2+12, 0)]:
        mnt = cq.Workplane("XY").center(ox, oy).cylinder(10, 5).translate((0, 0, H/2))
        box = box.union(mnt)

    return box


# ──────────────────────────────────────────────────────────────────────────────
# 9. Propeller guard
# ──────────────────────────────────────────────────────────────────────────────

def _propeller_guard(spec: dict) -> cq.Workplane:
    span      = spec.get("span_mm", 250)
    arm_count = int(spec.get("arm_count", 4))
    wall      = spec.get("wall_mm", 2.5)

    prop_r  = span / 4 * 0.55
    ring_t  = max(2, wall)
    hub_r   = max(20, span * 0.08)
    arm_w   = max(8, span * 0.035)
    arm_len = span / 2 - hub_r - prop_r

    # Hub
    guard = (
        cq.Workplane("XY")
        .cylinder(ring_t * 2, hub_r)
        .cut(cq.Workplane("XY").cylinder(ring_t * 2, hub_r - ring_t * 2))
    )

    angle_step = 360.0 / arm_count
    for i in range(arm_count):
        a  = math.radians(i * angle_step)
        # Arm
        cx = math.cos(a) * (hub_r + arm_len / 2)
        cy = math.sin(a) * (hub_r + arm_len / 2)
        arm = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, math.degrees(a)))
            .center(hub_r + arm_len / 2, 0)
            .rect(arm_len, arm_w)
            .extrude(ring_t)
        )
        guard = guard.union(arm)
        # Prop ring
        mx = math.cos(a) * (hub_r + arm_len + prop_r)
        my = math.sin(a) * (hub_r + arm_len + prop_r)
        ring = (
            cq.Workplane("XY")
            .center(mx, my)
            .cylinder(ring_t, prop_r + ring_t)
            .cut(cq.Workplane("XY").center(mx, my).cylinder(ring_t, prop_r))
        )
        guard = guard.union(ring)

    return guard


# ──────────────────────────────────────────────────────────────────────────────
# 10. Battery tray
# ──────────────────────────────────────────────────────────────────────────────

def _battery_tray(spec: dict) -> cq.Workplane:
    L    = spec.get("length_mm", 170)
    W    = spec.get("width_mm", 47)
    H    = spec.get("height_mm", 36)
    wall = spec.get("wall_mm", 2.0)

    tray = cq.Workplane("XY").box(L, W, H)
    inner = cq.Workplane("XY").box(L - wall*2, W - wall*2, H).translate((0, 0, wall))
    tray  = tray.cut(inner)

    # Velcro strap slots (2×)
    for ox in [-L/4, L/4]:
        slot = (
            cq.Workplane("XZ")
            .center(ox, 0)
            .rect(12, H + 2)
            .extrude(wall + 2)
            .translate((0, -W/2 - 1, 0))
        )
        tray = tray.cut(slot)

    # 4 mounting holes
    for (ox, oy) in [(L/2-8, W/2-8), (-L/2+8, W/2-8),
                     (L/2-8, -W/2+8), (-L/2+8, -W/2+8)]:
        hole = cq.Workplane("XY").center(ox, oy).cylinder(wall + 2, 2.5)
        tray = tray.cut(hole)

    # Side rails
    for sy in [-1, 1]:
        rail = (
            cq.Workplane("XY")
            .center(0, sy * (W/2 + 3))
            .box(L, 6, H * 0.4)
        )
        tray = tray.union(rail)

    return tray


# ──────────────────────────────────────────────────────────────────────────────
# 11. VTOL tilt-rotor mount
# ──────────────────────────────────────────────────────────────────────────────

def _vtol_mount(spec: dict) -> cq.Workplane:
    span = spec.get("span_mm", 300)
    wall = spec.get("wall_mm", 3.0)
    H    = spec.get("height_mm", 20)

    arm_l  = span * 0.45
    arm_w  = max(15, span * 0.055)
    pivot_r = arm_w * 0.6

    # Main spar
    spar = cq.Workplane("XY").box(arm_l * 2.2, arm_w, H)

    # Pivot housing at each end (allows 0-90° rotation)
    for sx in [-1, 1]:
        piv = (
            cq.Workplane("XY")
            .center(sx * arm_l, 0)
            .cylinder(H * 1.8, pivot_r + wall)
            .cut(cq.Workplane("XY").center(sx * arm_l, 0).cylinder(H * 1.8, pivot_r))
        )
        spar = spar.union(piv)

        # Rotor arm (shown at 45° = mid-transition)
        rot_arm = (
            cq.Workplane("YZ")
            .transformed(rotate=(45, 0, 0))
            .center(0, 0)
            .rect(arm_w * 0.7, span * 0.25)
            .extrude(wall)
            .translate((sx * arm_l, 0, 0))
        )
        spar = spar.union(rot_arm)

    # Servo mount tabs
    for sx in [-1, 1]:
        tab = (
            cq.Workplane("XY")
            .center(sx * arm_l * 0.6, arm_w * 0.8)
            .box(20, 12, H * 0.8)
        )
        spar = spar.union(tab)

    return spar


# ──────────────────────────────────────────────────────────────────────────────
# Safe last-resort fallback
# ──────────────────────────────────────────────────────────────────────────────

def _safe_fallback(spec: dict) -> cq.Workplane:
    span = max(50, spec.get("span_mm", 200))
    return (
        cq.Workplane("XY")
        .box(span * 0.3, span * 0.3, 10)
    )
