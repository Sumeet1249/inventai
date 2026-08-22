import cadquery as cq
import os

class GLTFExporter:
    @staticmethod
    def export(model: cq.Workplane, filename: str) -> str:
        """
        Exports a CadQuery model to GLTF format for web viewing.
        Note: Depending on cq version, this might export as STL/AMF first if GLTF isn't natively built-in,
        but recent OCP builds support GLB/GLTF.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        # We export as STL as fallback if GLTF isn't directly supported by the specific CQ version,
        # but modern cq.exporters support it if specified.
        try:
            cq.exporters.export(model, filename, exportType='GLTF')
        except Exception:
            # Fallback to STL for demo if GLTF fails in this environment
            stl_file = filename.replace('.gltf', '.stl')
            cq.exporters.export(model, stl_file)
            return stl_file
            
        return filename
