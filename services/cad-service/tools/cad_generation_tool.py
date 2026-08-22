from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from services.cad_service.generators.cadquery_generator import CadQueryGenerator

class CADGenInput(BaseModel):
    template_type: str = Field(description="The CAD template to use (e.g., 'box', 'cylinder').")
    parameters: Dict[str, float] = Field(description="The numerical parameters extracted from the prompt.")

class CADGenOutput(BaseModel):
    success: bool
    model_data: Dict[str, Any]

class CADGenerationTool(BaseTool):
    """
    Connects the AI Core to the CadQuery Python Generator.
    Converts AI-extracted parameters into physical geometry.
    """
    name = "cad_generation"
    description = "Generates parametric CAD models based on extracted engineering requirements."
    tags = ["cad", "generation", "geometry"]
    input_schema = CADGenInput
    output_schema = CADGenOutput

    async def execute(self, inputs: CADGenInput, context: ToolContext) -> CADGenOutput:
        try:
            model = CadQueryGenerator.generate_from_parameters(
                inputs.template_type, 
                inputs.parameters
            )
            return CADGenOutput(success=True, model_data={"status": "generated", "info": "Workplane object created"})
        except Exception as e:
            return CADGenOutput(success=False, model_data={"error": str(e)})
