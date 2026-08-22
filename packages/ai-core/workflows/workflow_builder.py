from langgraph.graph import StateGraph, END
from packages.ai_core.workflows.state import WorkflowState
from packages.ai_core.workflows.router import TaskRouter

class WorkflowBuilder:
    """
    Factory class for building complex LangGraph state machines.
    Supports both the standard node pattern and custom node/edge wiring.
    """
    def __init__(self):
        self.workflow = StateGraph(WorkflowState)
        self.nodes = {}

    # ── Delegation helpers so callers can use builder like a StateGraph ──────

    def add_node(self, name: str, fn):
        self.workflow.add_node(name, fn)
        return self

    def add_edge(self, from_node: str, to_node: str):
        self.workflow.add_edge(from_node, to_node)
        return self

    def add_conditional_edges(self, from_node: str, router_fn, mapping: dict):
        self.workflow.add_conditional_edges(from_node, router_fn, mapping)
        return self

    def set_entry_point(self, node: str):
        self.workflow.set_entry_point(node)
        return self

    def set_finish_point(self, node: str):
        self.workflow.add_edge(node, END)
        return self

    # ── Standard pre-wired pattern ───────────────────────────────────────────

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
                "fallback": END,
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
                "fallback": END,
            }
        )

        self.workflow.add_edge("retry", "planner")
        self.workflow.add_edge("reviewer", END)
        return self

    def compile(self, checkpointer=None, interrupt_before=None):
        return self.workflow.compile(
            checkpointer=checkpointer,
            interrupt_before=interrupt_before,
        )
