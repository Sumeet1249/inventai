class MaterialDatabase:
    """
    Standard material library for physics simulations.
    Properties:
    - E: Young's Modulus (GPa)
    - nu: Poisson's Ratio
    - rho: Density (kg/m^3)
    - yield_strength: Yield Strength (MPa)
    """
    
    MATERIALS = {
        "aluminum": {
            "name": "Aluminum 6061",
            "E": 69.0,
            "nu": 0.33,
            "rho": 2700,
            "yield_strength": 276
        },
        "carbon_fiber": {
            "name": "Carbon Fiber Composite",
            "E": 150.0,
            "nu": 0.28,
            "rho": 1600,
            "yield_strength": 600
        },
        "abs": {
            "name": "ABS Plastic",
            "E": 2.3,
            "nu": 0.35,
            "rho": 1040,
            "yield_strength": 40
        },
        "pla": {
            "name": "PLA Plastic",
            "E": 3.5,
            "nu": 0.36,
            "rho": 1250,
            "yield_strength": 50
        },
        "titanium": {
            "name": "Titanium Grade 5",
            "E": 113.8,
            "nu": 0.34,
            "rho": 4430,
            "yield_strength": 880
        }
    }
    
    @classmethod
    def get_material(cls, material_id: str) -> dict:
        material_id = material_id.lower().replace(" ", "_")
        if material_id in cls.MATERIALS:
            return cls.MATERIALS[material_id]
        # Default to Aluminum if unknown
        return cls.MATERIALS["aluminum"]
