from langgraph.graph import StateGraph, END
from packages.ai_core.workflows.base_workflow import BaseWorkflow
from packages.ai_core.interfaces.core_interfaces import BaseCheckpoint
from packages.ai_core.utils.error_recovery import fallback_recovery_node, route_on_error
from langgraph.prebuilt import ToolNode

class EnterpriseLangGraphWorkflow(BaseWorkflow):
    """
    Standardizes the creation of the Planner -> Executor -> Reviewer cycle.
    """
    def __init__(self, state_schema: type, checkpointer: BaseCheckpoint):
        self.workflow = StateGraph(state_schema)
        self.checkpointer = checkpointer.get_saver()

    def build(self, planner_node, executor_node, tools: list):
        # Add Nodes
        self.workflow.add_node("planner", planner_node)
        self.workflow.add_node("executor", executor_node)
        self.workflow.add_node("tools", ToolNode(tools))
        self.workflow.add_node("fallback", fallback_recovery_node)
        
        # Edges
        self.workflow.set_entry_point("planner")
        
        # Conditional Routing for Planner
        self.workflow.add_conditional_edges(
            "planner",
            route_on_error,
            {
                "continue": "executor",
                "retry": "planner",
                "fallback": "fallback"
            }
        )
        
        # Standard Tool loop
        self.workflow.add_edge("tools", "executor")
        
        # End points
        self.workflow.add_edge("fallback", END)
        return self

    def compile(self):
        return self.workflow.compile(checkpointer=self.checkpointer)
