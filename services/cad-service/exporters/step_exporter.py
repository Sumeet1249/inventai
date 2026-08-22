import cadquery as cq
import os

class StepExporter:
    @staticmethod
    def export(model: cq.Workplane, filename: str) -> str:
        """
        Exports a CadQuery model to STEP format.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        cq.exporters.export(model, filename)
        return filename
