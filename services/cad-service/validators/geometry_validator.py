import cadquery as cq

class GeometryValidationError(Exception):
    pass

class GeometryValidator:
    """Validates CadQuery models before export."""
    
    @staticmethod
    def validate(model: cq.Workplane):
        """
        Runs heuristics to ensure the geometry is valid.
        """
        # 1. Zero-volume check
        try:
            vol = model.val().Volume()
            if vol <= 0:
                raise GeometryValidationError("Generated CAD model has zero or negative volume.")
        except Exception as e:
            if isinstance(e, GeometryValidationError):
                raise
            raise GeometryValidationError(f"Volume calculation failed: {e}")
            
        # 2. Bounding Box extraction
        try:
            bbox = model.val().BoundingBox()
            if bbox.xlen == 0 or bbox.ylen == 0 or bbox.zlen == 0:
                raise GeometryValidationError("Generated CAD model is infinitely thin in one or more dimensions.")
            
            # Example heuristic: nothing should exceed a 2x2x2 meter build volume (2000mm)
            if bbox.xlen > 2000 or bbox.ylen > 2000 or bbox.zlen > 2000:
                raise GeometryValidationError("Generated CAD model exceeds maximum manufacturing dimensions.")
                
        except Exception as e:
            if isinstance(e, GeometryValidationError):
                raise
            raise GeometryValidationError(f"Bounding box calculation failed: {e}")
                
        return True
