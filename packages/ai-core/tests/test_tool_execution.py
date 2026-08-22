import pytest
from pydantic import BaseModel
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from packages.ai_core.tools.executor import ToolExecutor
from packages.ai_core.tools.exceptions import ToolPermissionError

class DummyInput(BaseModel):
    query: str

class DummyOutput(BaseModel):
    result: str

class DummyTool(BaseTool):
    name = "dummy_search"
    description = "Searches for dummy data."
    tags = ["admin"]
    input_schema = DummyInput
    output_schema = DummyOutput

    async def execute(self, inputs: DummyInput, context: ToolContext) -> DummyOutput:
        return DummyOutput(result=f"Found: {inputs.query}")

@pytest.mark.asyncio
async def test_tool_permissions():
    """Validates that tools with specific tags reject unauthorized contexts."""
    tool = DummyTool()
    
    # Authorized Context
    auth_ctx = ToolContext(session_id="1", workflow_id="1", agent_id="agent1", roles=["admin"])
    result = await ToolExecutor.execute(tool, {"query": "test"}, auth_ctx)
    assert result.success is True
    
    # Unauthorized Context
    unauth_ctx = ToolContext(session_id="2", workflow_id="2", agent_id="agent2", roles=["user"])
    with pytest.raises(ToolPermissionError):
        await ToolExecutor.execute(tool, {"query": "test"}, unauth_ctx)
