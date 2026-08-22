from typing import Dict, Any
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from services.cad_service.tools.cad_generation_tool import CADGenerationTool
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.memory.memory_manager import MemoryManager

def build_cad_orchestration_workflow(memory_manager: MemoryManager):
    """
    Builds the LangGraph orchestration for the CAD Generator pipeline.
    """
    builder = WorkflowBuilder()

    # Tools
    cad_tool = CADGenerationTool()

    # Agents
    context = AgentContext(agent_id="cad_orchestrator", role="coordinator")
    planner = AgentFactory.create_agent("planner", context, memory_manager)
    reviewer = AgentFactory.create_agent("reviewer", context, memory_manager)

    async def plan_cad_parameters(state: WorkflowState):
        plan = await planner.execute({"task": f"Extract CAD parameters from: {state.input_data.get('prompt')}"})
        state.metadata["cad_params"] = {"template_type": "box", "parameters": {"length": 10, "width": 5, "height": 2}}
        return {"metadata": state.metadata}

    async def generate_cad(state: WorkflowState):
        # We would execute CADGenerationTool here
        state.metadata["cad_model"] = {"type": "box"}
        return {"metadata": state.metadata}

    async def review_geometry(state: WorkflowState):
        # We would use GeometryValidator and ReviewerAgent
        state.output_data = {"status": "Validated", "model": state.metadata["cad_model"]}
        return {"output_data": state.output_data}

    builder.add_node("plan", plan_cad_parameters)
    builder.add_node("generate", generate_cad)
    builder.add_node("review", review_geometry)

    builder.set_entry_point("plan")
    builder.add_edge("plan", "generate")
    builder.add_edge("generate", "review")
    builder.set_finish_point("review")

    return builder.compile()
