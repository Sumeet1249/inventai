import cadquery as cq
from services.cad_service.generators.frame import generate_frame
from services.cad_service.generators.battery import generate_battery
from services.cad_service.generators.enclosure import generate_enclosure

def generate_drone(params: dict) -> cq.Workplane:
    """
    Parametrically generates a drone by assembling modular components.
    """
    # 1. Base Frame
    drone = generate_frame(params)
    
    # 2. Battery pack
    if params.get("battery_compartment", True):
        battery = generate_battery(params)
        # Position battery underneath the frame
        battery = battery.translate((0, 0, -20))
        drone = drone.union(battery)
        
    # 3. Enclosure
    enclosure_params = {
        "enclosure_radius": params.get("span_mm", 400) * 0.15,
        "enclosure_height": 30
    }
    enclosure = generate_enclosure(enclosure_params)
    # Position enclosure on top of the frame
    enclosure = enclosure.translate((0, 0, 10))
    drone = drone.union(enclosure)
        
    return drone

