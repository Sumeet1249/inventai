import pytest
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.agents.agent_state import AgentState
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider
from typing import Dict, Any, Optional

class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key: str) -> Optional[Dict[str, Any]]: return None
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None): pass
    async def delete(self, key: str): pass

@pytest.mark.asyncio
async def test_planner_agent_lifecycle():
    manager = MemoryManager(MockMemoryProvider())
    context = AgentContext(agent_id="test_planner", role="planner", permissions=["admin"])
    
    # Factory instantiates PlannerAgent and injects models/memory
    planner = AgentFactory.create_agent("planner", context, manager)
    
    assert "task_decomposition" in planner.get_capabilities()
    
    state = AgentState(session_id="s1").model_dump()
    result = await planner.execute(state)
    
    assert "plan" in result
    assert result["plan"] == ["step_1", "step_2"]
