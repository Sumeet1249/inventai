from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

# --- Abstracting HTTP calls to Microservices ---

class MicroserviceInput(BaseModel):
    payload: Dict[str, Any]

class MicroserviceOutput(BaseModel):
    success: bool
    data: Dict[str, Any]

class CallPatentServiceTool(BaseTool):
    name = "call_patent_service"
    description = "Triggers the Patent Intelligence Engine via HTTP."
    input_schema = MicroserviceInput
    output_schema = MicroserviceOutput

    async def execute(self, inputs: MicroserviceInput, context: ToolContext) -> MicroserviceOutput:
        # Mock HTTP call to services/patent-service
        return MicroserviceOutput(success=True, data={"patent_score": 0.85})

class CallCADServiceTool(BaseTool):
    name = "call_cad_service"
    description = "Triggers the CAD Intelligence Engine via HTTP."
    input_schema = MicroserviceInput
    output_schema = MicroserviceOutput

    async def execute(self, inputs: MicroserviceInput, context: ToolContext) -> MicroserviceOutput:
        # Mock HTTP call to services/cad-service
        return MicroserviceOutput(success=True, data={"model_id": "cad_123", "status": "generated"})
