import cadquery as cq
import logging
import os

logger = logging.getLogger(__name__)

class MeshExporter:
    """
    Handles exporting CadQuery assemblies/parts into various formats.
    """
    @staticmethod
    def export_step(cq_model: any, file_path: str):
        """Exports to STEP format for manufacturing."""
        try:
            cq.exporters.export(cq_model, file_path, "STEP")
        except Exception as e:
            logger.error(f"Failed to export STEP: {e}")

    @staticmethod
    def export_stl(cq_model: any, file_path: str):
        """Exports to STL for 3D printing and Three.js preview."""
        try:
            cq.exporters.export(cq_model, file_path, "STL")
        except Exception as e:
            logger.error(f"Failed to export STL: {e}")

    @staticmethod
    def export_gltf(cq_model: any, file_path: str):
        """Exports to GLTF/GLB for web-based Three.js viewers."""
        # Cadquery natively doesn't export GLTF. We can use STL for the UI or try VTK/SVG.
        # But we can export as STL and copy it over as a workaround if Three.js accepts STL.
        try:
            # Many frontends can handle STL in place of GLTF if properly loaded
            # We'll just write it as STL for now.
            cq.exporters.export(cq_model, file_path.replace(".gltf", ".stl"), "STL")
        except Exception as e:
            logger.error(f"Failed to export GLTF (fallback STL): {e}")
