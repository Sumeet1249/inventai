class MaterialLibrary:
    """
    Database of material properties required for physical simulation.
    """
    MATERIALS = {
        "steel_304": {
            "youngs_modulus_gpa": 193,
            "poissons_ratio": 0.29,
            "yield_strength_mpa": 215,
            "thermal_conductivity_w_mk": 16.2
        },
        "aluminum_6061": {
            "youngs_modulus_gpa": 69,
            "poissons_ratio": 0.33,
            "yield_strength_mpa": 276,
            "thermal_conductivity_w_mk": 167
        }
    }

    @staticmethod
    def get_properties(material_id: str) -> dict:
        if material_id not in MaterialLibrary.MATERIALS:
            raise ValueError(f"Material {material_id} not found in library.")
        return MaterialLibrary.MATERIALS[material_id]
