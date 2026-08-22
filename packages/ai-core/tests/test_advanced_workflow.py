import pytest
import asyncio
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.planner import PlannerNode
from packages.ai_core.workflows.executor import ExecutorNode
from packages.ai_core.workflows.reviewer import ReviewerNode
from packages.ai_core.workflows.retry import RetryNode
from packages.ai_core.workflows.workflow import ExecutionEngine

@pytest.mark.asyncio
async def test_workflow_engine_execution():
    """
    Validates that the WorkflowBuilder successfully creates a StateGraph
    and the ExecutionEngine can run it asynchronously without crashing.
    """
    
    # Mock Agents
    async def mock_agent(state): return {"plan": ["task_1"]}
    async def mock_reviewer(state): return {"final_output": "success"}

    builder = WorkflowBuilder()
    builder.add_standard_nodes(
        planner=PlannerNode(mock_agent),
        executor=ExecutorNode(tool_executor=None),
        reviewer=ReviewerNode(reviewer_agent=mock_reviewer),
        retry=RetryNode()
    )
    builder.build_standard_edges()
    
    app = builder.compile()
    engine = ExecutionEngine(app)
    
    initial_state = {"messages": [], "workflow_id": "test_123"}
    final_state = await engine.execute_async(initial_state)
    
    assert final_state is not None
    assert final_state["current_task"] == "task_1"
    assert "task_1" in final_state["tasks_completed"]
