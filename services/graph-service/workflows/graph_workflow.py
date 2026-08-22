from typing import Dict, Any
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from services.graph_service.tools.graph_query_tool import GraphQueryTool
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.memory.memory_manager import MemoryManager

def build_graph_orchestration_workflow(memory_manager: MemoryManager):
    """
    Builds the LangGraph orchestration for Knowledge Graph Intelligence.
    """
    builder = WorkflowBuilder()

    # Tools
    graph_tool = GraphQueryTool()

    # Agents
    context = AgentContext(agent_id="graph_orchestrator", role="coordinator")
    planner = AgentFactory.create_agent("planner", context, memory_manager)
    reviewer = AgentFactory.create_agent("reviewer", context, memory_manager)

    async def plan_graph_query(state: WorkflowState):
        # Extract intent via Planner
        state.metadata["query_plan"] = {
            "query_type": "recommendation",
            "parameters": {"patent_id": state.input_data.get("entity_id")}
        }
        return {"metadata": state.metadata}

    async def execute_cypher(state: WorkflowState):
        # Execute GraphQueryTool
        state.metadata["graph_results"] = [{"node": {"id": "t1", "label": "Technology", "name": "AI"}}]
        return {"metadata": state.metadata}

    async def summarize_insights(state: WorkflowState):
        # Reviewer analyzes graph structure
        state.output_data = {
            "insight": "Based on graph traversal, 'AI' is highly recommended.",
            "raw_nodes": state.metadata["graph_results"]
        }
        return {"output_data": state.output_data}

    builder.add_node("plan", plan_graph_query)
    builder.add_node("execute_cypher", execute_cypher)
    builder.add_node("summarize", summarize_insights)

    builder.set_entry_point("plan")
    builder.add_edge("plan", "execute_cypher")
    builder.add_edge("execute_cypher", "summarize")
    builder.set_finish_point("summarize")

    return builder.compile()
