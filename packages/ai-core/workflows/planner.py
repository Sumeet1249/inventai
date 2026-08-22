from packages.ai_core.workflows.interfaces import BaseWorkflowNode
from packages.ai_core.workflows.state import WorkflowState
from packages.ai_core.workflows.events import publish_workflow_event
import time

class PlannerNode(BaseWorkflowNode):
    """
    Responsible for decomposing complex workflows into a plan.
    """
    def __init__(self, llm_agent):
        self.llm_agent = llm_agent

    async def __call__(self, state: WorkflowState) -> dict:
        await publish_workflow_event("node_started", node="planner", workflow_id=state.get("workflow_id"))
        
        # In a real scenario, this would call self.llm_agent to parse messages and return a plan.
        # We reuse the agent implementation here abstractly.
        result = await self.llm_agent(state)
        
        await publish_workflow_event("node_finished", node="planner", workflow_id=state.get("workflow_id"))
        
        return {
            "plan": result.get("plan", []),
            "tasks_completed": [],
            "start_time": state.get("start_time", time.time())
        }
