import cadquery as cq

class CadQueryGenerator:
    """
    Parametric CAD generation engine leveraging CadQuery.
    """
    @staticmethod
    def generate_box(length: float, width: float, height: float):
        """Generates a simple box."""
        return cq.Workplane("XY").box(length, width, height)

    @staticmethod
    def generate_cylinder(radius: float, height: float):
        """Generates a cylinder."""
        return cq.Workplane("XY").circle(radius).extrude(height)

    @staticmethod
    def generate_from_parameters(template_type: str, parameters: dict):
        """Dynamic generation based on AI-extracted parameters."""
        if template_type == "box":
            return CadQueryGenerator.generate_box(
                parameters.get("length", 10),
                parameters.get("width", 10),
                parameters.get("height", 10)
            )
        elif template_type == "cylinder":
            return CadQueryGenerator.generate_cylinder(
                parameters.get("radius", 5),
                parameters.get("height", 10)
            )
        else:
            raise ValueError(f"Unknown CAD template type: {template_type}")
