import pytest
import cadquery as cq
from services.cad_service.validators.geometry_validator import GeometryValidator, GeometryValidationError

def test_geometry_validator_passes():
    # Create a valid 10x10x10 box
    valid_model = cq.Workplane("XY").box(10, 10, 10)
    assert GeometryValidator.validate(valid_model) is True

def test_geometry_validator_zero_volume():
    # Create an empty model (or a 2D sketch not extruded)
    invalid_model = cq.Workplane("XY").circle(10)
    
    with pytest.raises(GeometryValidationError) as exc:
        GeometryValidator.validate(invalid_model)
    assert "zero or negative volume" in str(exc.value)

def test_geometry_validator_exceeds_bounds():
    # Create a massive model (3000mm)
    massive_model = cq.Workplane("XY").box(3000, 10, 10)
    
    with pytest.raises(GeometryValidationError) as exc:
        GeometryValidator.validate(massive_model)
    assert "exceeds maximum manufacturing dimensions" in str(exc.value)
