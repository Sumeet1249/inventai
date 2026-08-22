import os
import tempfile
import logging
import cadquery as cq

logger = logging.getLogger(__name__)


class GLTFExporter:
    @staticmethod
    def export(model: cq.Workplane, filename: str) -> str:
        """
        Exports a CadQuery model to a valid GLTF 2.0 file.

        Strategy:
          1. Export the CadQuery geometry to a temporary STL file (universally
             supported by all cadquery versions).
          2. Load the STL into trimesh and re-export as GLTF 2.0 — which
             Three.js / GLTFLoader requires.

        This avoids the silent fallback bug in the old implementation where
        cadquery's exportType='GLTF' would throw (unsupported in cq 2.4) and
        the except block wrote STL bytes to a .gltf path, causing the
        "Unsupported asset" error in Three.js.
        """
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # ── Step 1: CadQuery → STL (always works) ──────────────────────────
        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            stl_path = tmp.name

        try:
            cq.exporters.export(model, stl_path)
            logger.debug("STL intermediate written to %s", stl_path)

            # ── Step 2: STL → GLTF 2.0 via trimesh ────────────────────────
            import trimesh

            mesh = trimesh.load(stl_path, force="mesh")

            # Apply a neutral grey material so the model renders correctly
            # in Three.js without requiring a separate material file.
            mesh.visual = trimesh.visual.ColorVisuals(
                mesh=mesh,
                vertex_colors=[180, 180, 190, 255],  # RGBA
            )

            # trimesh.exchange.export.export_mesh writes a valid GLTF 2.0
            # JSON (not GLB) when the extension is .gltf.
            gltf_bytes = trimesh.exchange.gltf.export_gltf(
                trimesh.Scene(geometry={"model": mesh}),
            )

            # export_gltf returns a dict of {filename: bytes}; the main entry
            # is always the key that ends with .gltf
            gltf_key = next(
                (k for k in gltf_bytes if k.endswith(".gltf")),
                list(gltf_bytes.keys())[0],
            )

            with open(filename, "wb") as f:
                f.write(gltf_bytes[gltf_key])

            # Write any companion .bin buffers next to the .gltf file
            out_dir = os.path.dirname(filename)
            for key, data in gltf_bytes.items():
                if key == gltf_key:
                    continue
                companion_path = os.path.join(out_dir, key)
                with open(companion_path, "wb") as f:
                    f.write(data)
                logger.debug("GLTF companion buffer written: %s", companion_path)

            logger.info("GLTF 2.0 exported successfully: %s", filename)
            return filename

        except Exception as exc:
            logger.error("GLTF export failed: %s", exc, exc_info=True)
            # Last-resort fallback: return a valid STL so the frontend at
            # least has something, rather than silently writing STL bytes
            # to a .gltf path and confusing Three.js.
            stl_out = filename.replace(".gltf", ".stl")
            try:
                cq.exporters.export(model, stl_out)
                logger.warning("Fell back to STL export: %s", stl_out)
            except Exception as stl_exc:
                logger.error("STL fallback also failed: %s", stl_exc)
            return stl_out

        finally:
            # Always clean up the temp STL
            if os.path.exists(stl_path):
                os.unlink(stl_path)
