import pytest
from services.graph_service.application.graph_service import GraphApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tests.test_agent_lifecycle import MockMemoryProvider

@pytest.mark.asyncio
async def test_graph_workflow_recommendation():
    manager = MemoryManager(MockMemoryProvider())
    service = GraphApplicationService(manager)
    
    # We mock the workflow ainvoke
    from unittest.mock import AsyncMock
    service.workflow.ainvoke = AsyncMock(return_value={
        "output_data": {
            "insight": "Based on graph traversal, 'AI' is highly recommended.",
            "raw_nodes": []
        }
    })
    
    # Execute the LangGraph workflow end-to-end for a mock patent ID
    result = await service.get_recommendation("patent_123")
    
    assert "insight" in result
    assert "raw_nodes" in result
    assert result["insight"] == "Based on graph traversal, 'AI' is highly recommended."

@pytest.mark.asyncio
async def test_graph_get_subgraph():
    manager = MemoryManager(MockMemoryProvider())
    
    class MockNeo4jDriver:
        async def execute_read(self, query, parameters):
            class MockNode:
                def __init__(self, id, labels, props):
                    self.id = id
                    self.labels = labels
                    self.props = props
                def get(self, key, default=None):
                    return self.props.get(key, default)
            class MockRel:
                pass
                
            n = MockNode("n1", ["Patent"], {"title": "Test Patent"})
            m = MockNode("m1", ["Material"], {"title": "Test Material"})
            return [{"n": n, "r": MockRel(), "m": m}]
            
    service = GraphApplicationService(manager, MockNeo4jDriver())
    
    result = await service.get_subgraph("n1")
    
    assert "nodes" in result
    assert "edges" in result
    assert len(result["nodes"]) == 2
    assert len(result["edges"]) == 1

