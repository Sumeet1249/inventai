from typing import Dict, Any
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.memory.memory_manager import MemoryManager
# Import agents so their @AgentRegistry.register decorators fire before AgentFactory is called
from packages.ai_core.agents.planner_agent import PlannerAgent   # noqa: F401 - side-effect import
from packages.ai_core.agents.agent_factory import AgentFactory


def build_graph_orchestration_workflow(memory_manager: MemoryManager):
    """
    Builds the LangGraph orchestration for Knowledge Graph Intelligence.
    """
    builder = WorkflowBuilder()

    async def plan_graph_query(state: WorkflowState) -> Dict[str, Any]:
        metadata = state.get("metadata") or {}
        input_data = state.get("input_data") or {}
        metadata["query_plan"] = {
            "query_type": "recommendation",
            "parameters": {"entity_id": input_data.get("entity_id")},
        }
        return {"metadata": metadata}

    async def execute_cypher(state: WorkflowState) -> Dict[str, Any]:
        metadata = state.get("metadata") or {}
        metadata["graph_results"] = [
            {"node": {"id": "t1", "label": "Technology", "name": "AI"}}
        ]
        return {"metadata": metadata}

    async def summarize_insights(state: WorkflowState) -> Dict[str, Any]:
        metadata = state.get("metadata") or {}
        output_data = {
            "insight": "Based on graph traversal, 'AI' is highly recommended.",
            "raw_nodes": metadata.get("graph_results", []),
        }
        return {"output_data": output_data}

    builder.add_node("plan", plan_graph_query)
    builder.add_node("execute_cypher", execute_cypher)
    builder.add_node("summarize", summarize_insights)

    builder.set_entry_point("plan")
    builder.add_edge("plan", "execute_cypher")
    builder.add_edge("execute_cypher", "summarize")
    builder.set_finish_point("summarize")

    return builder.compile()
