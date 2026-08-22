import cadquery as cq

def generate_battery(params: dict) -> cq.Workplane:
    """Generates a parametric Li-Po battery block."""
    length = params.get("battery_length", 80)
    width = params.get("battery_width", 40)
    height = params.get("battery_height", 20)
    
    battery = cq.Workplane("XY").box(length, width, height)
    # Fillet edges to simulate shrink wrap
    battery = battery.edges("|Z").fillet(2)
    return battery
