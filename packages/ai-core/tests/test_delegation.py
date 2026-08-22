import pytest
from packages.ai_core.agents.exceptions import AgentExecutionError
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tests.test_agent_lifecycle import MockMemoryProvider

@pytest.mark.asyncio
async def test_delegation_depth_limit():
    manager = MemoryManager(MockMemoryProvider())
    context = AgentContext(agent_id="test_router", role="router")
    
    router = AgentFactory.create_agent("router", context, manager)
    
    # Simulate a state that has been delegated too many times
    state = {"delegation_depth": 10, "session_id": "s1"}
    
    with pytest.raises(AgentExecutionError, match="Max delegation depth exceeded"):
        await router.execute(state)
