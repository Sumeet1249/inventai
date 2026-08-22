from typing import Dict, Any
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from services.innovation_engine.orchestrator.service_tools import CallPatentServiceTool, CallCADServiceTool
from services.innovation_engine.events.event_bus import event_bus, WorkflowEvent
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.memory.memory_manager import MemoryManager

def build_master_innovation_workflow(memory_manager: MemoryManager):
    """
    Builds the Master LangGraph orchestration that ties the entire InventAI platform together.
    Sequence: Patent -> Research -> Graph -> CAD -> Physics
    """
    builder = WorkflowBuilder()

    # Tools for microservice orchestration
    patent_tool = CallPatentServiceTool()
    cad_tool = CallCADServiceTool()

    # Master Agents
    context = AgentContext(agent_id="master_orchestrator", role="coordinator")
    master_planner = AgentFactory.create_agent("planner", context, memory_manager)

    async def execute_patent_phase(state: WorkflowState):
        await event_bus.publish(WorkflowEvent(project_id=state.workflow_id, event_type="NodeStarted", node="PatentIntelligence"))
        # Execute cross-service tool
        res = await patent_tool.execute({"payload": {"idea": state.input_data.get("idea")}}, None)
        state.metadata["patent_data"] = res.data
        await event_bus.publish(WorkflowEvent(project_id=state.workflow_id, event_type="NodeCompleted", node="PatentIntelligence"))
        return {"metadata": state.metadata}

    async def execute_cad_phase(state: WorkflowState):
        await event_bus.publish(WorkflowEvent(project_id=state.workflow_id, event_type="NodeStarted", node="CADIntelligence"))
        # Pass patent parameters to CAD
        res = await cad_tool.execute({"payload": {"parameters": state.metadata.get("patent_data")}}, None)
        state.metadata["cad_data"] = res.data
        await event_bus.publish(WorkflowEvent(project_id=state.workflow_id, event_type="NodeCompleted", node="CADIntelligence"))
        return {"metadata": state.metadata}

    async def finalize_project(state: WorkflowState):
        await event_bus.publish(WorkflowEvent(project_id=state.workflow_id, event_type="WorkflowCompleted", node="Finalize"))
        state.output_data = {"status": "Complete", "artifacts": state.metadata}
        return {"output_data": state.output_data}

    # Construct Master Graph (Simplified sequence for demonstration)
    builder.add_node("patent", execute_patent_phase)
    builder.add_node("cad", execute_cad_phase)
    builder.add_node("finalize", finalize_project)

    builder.set_entry_point("patent")
    builder.add_edge("patent", "cad")
    builder.add_edge("cad", "finalize")
    builder.set_finish_point("finalize")

    return builder.compile()
