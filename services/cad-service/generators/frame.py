import cadquery as cq

def generate_frame(params: dict) -> cq.Workplane:
    """Generates the main structural cross-frame."""
    span = params.get("span_mm", 400)
    motor_count = params.get("motor_count", 4)
    arm_width = params.get("arm_width", 20)
    
    chassis = cq.Workplane("XY").box(span * 0.2, span * 0.2, 10)
    
    angle_step = 360 / motor_count
    for i in range(motor_count):
        angle = i * angle_step
        arm = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle))
            .center(0, 0)
            .rect(arm_width, span * 0.4)
            .extrude(8)
            .translate((0, span * 0.2, 0))
        )
        chassis = chassis.union(arm)
        
        # Add motor mount at end of arm
        mount = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle))
            .center(0, span * 0.4)
            .circle(arm_width * 0.8)
            .extrude(12)
        )
        chassis = chassis.union(mount)
        
    return chassis
