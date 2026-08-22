from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from services.physics_service.simulations.deepxde_solver import DeepXDESolver
from services.physics_service.materials.material_library import MaterialLibrary

class PhysicsSimInput(BaseModel):
    simulation_type: str = Field(description="'stress' or 'thermal'")
    boundary_conditions: Dict[str, Any] = Field(description="Forces and fixed points")
    material_id: str = Field(description="Material identifier (e.g., 'steel_304')")

class PhysicsSimOutput(BaseModel):
    success: bool
    results: Dict[str, Any]

class PhysicsSimulationTool(BaseTool):
    """
    Connects the AI Core to the DeepXDE Simulator.
    Executes PINNs to evaluate stress and thermal properties.
    """
    name = "physics_simulation"
    description = "Executes DeepXDE physics-informed neural networks to validate geometry."
    tags = ["physics", "simulation", "pinn"]
    input_schema = PhysicsSimInput
    output_schema = PhysicsSimOutput

    async def execute(self, inputs: PhysicsSimInput, context: ToolContext) -> PhysicsSimOutput:
        try:
            mat_props = MaterialLibrary.get_properties(inputs.material_id)
            
            if inputs.simulation_type == "stress":
                res = DeepXDESolver.run_stress_analysis({}, inputs.boundary_conditions, mat_props)
            elif inputs.simulation_type == "thermal":
                res = DeepXDESolver.run_thermal_analysis({}, inputs.boundary_conditions, mat_props)
            else:
                raise ValueError("Unknown simulation type.")
                
            return PhysicsSimOutput(success=True, results=res)
        except Exception as e:
            return PhysicsSimOutput(success=False, results={"error": str(e)})
