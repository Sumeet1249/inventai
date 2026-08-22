import cadquery as cq

def generate_enclosure(params: dict) -> cq.Workplane:
    """Generates a shelled dome enclosure."""
    radius = params.get("enclosure_radius", 50)
    height = params.get("enclosure_height", 30)
    
    enclosure = cq.Workplane("XY").circle(radius).extrude(height)
    # Add a top dome with a safe fillet radius
    safe_fillet = min(radius * 0.2, height * 0.4)
    enclosure = enclosure.faces(">Z").fillet(safe_fillet)
    # Shell it to make it hollow
    enclosure = enclosure.faces("<Z").shell(-2)
    return enclosure
