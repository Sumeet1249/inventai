import cadquery as cq
import os

class STLExporter:
    @staticmethod
    def export(model: cq.Workplane, filename: str) -> str:
        """
        Exports a CadQuery model to STL format for 3D printing.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        cq.exporters.export(model, filename)
        return filename
