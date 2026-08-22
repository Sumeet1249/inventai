from langgraph.graph import StateGraph, END
from packages.ai_core.workflows.state import WorkflowState
from packages.ai_core.workflows.router import TaskRouter

class WorkflowBuilder:
    """
    Factory class for building complex LangGraph state machines.
    """
    def __init__(self):
        self.workflow = StateGraph(WorkflowState)
        self.nodes = {}

    def add_standard_nodes(self, planner, executor, reviewer, retry):
        self.workflow.add_node("planner", planner)
        self.workflow.add_node("executor", executor)
        self.workflow.add_node("reviewer", reviewer)
        self.workflow.add_node("retry", retry)
        return self

    def build_standard_edges(self):
        router = TaskRouter()
        
        self.workflow.set_entry_point("planner")
        
        # Planner routing
        self.workflow.add_conditional_edges(
            "planner",
            router.route,
            {
                "executor": "executor",
                "retry": "retry",
                "fallback": END # Simplified
            }
        )
        
        # Executor routing
        self.workflow.add_conditional_edges(
            "executor",
            router.route,
            {
                "executor": "executor",
                "reviewer": "reviewer",
                "retry": "retry",
                "fallback": END
            }
        )
        
        self.workflow.add_edge("retry", "planner") # Retry loops back
        self.workflow.add_edge("reviewer", END)
        
        return self

    def compile(self, checkpointer=None, interrupt_before=None):
        return self.workflow.compile(
            checkpointer=checkpointer,
            interrupt_before=interrupt_before
        )
