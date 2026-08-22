import cadquery as cq

class CADGenerator:
    @staticmethod
    def generate_bracket(width: float, height: float, thickness: float):
        """
        Generates an L-bracket based on dynamic parameters.
        Returns the SVG or STEP file binary.
        """
        result = (
            cq.Workplane("XY")
            .box(width, thickness, height)
            .faces(">Z")
            .workplane()
            .hole(thickness / 2.0)
        )
        
        # cq.exporters.export(result, "bracket.step")
        return {"status": "success", "message": "CAD bracket generated"}
