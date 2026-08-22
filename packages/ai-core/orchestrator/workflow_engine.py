from langgraph.graph import StateGraph
from packages.ai_core.memory.checkpointer import CheckpointManager

class WorkflowEngine:
    """
    A wrapper around LangGraph's StateGraph to standardize workflow creation
    across different microservices.
    """
    def __init__(self, state_schema: type):
        self.workflow = StateGraph(state_schema)
        self.nodes = []

    def add_agent(self, name: str, agent_callable):
        self.workflow.add_node(name, agent_callable)
        self.nodes.append(name)
        return self

    def set_entry_point(self, node_name: str):
        self.workflow.set_entry_point(node_name)
        return self

    def add_edge(self, source: str, target: str):
        self.workflow.add_edge(source, target)
        return self
        
    def add_conditional_edge(self, source: str, condition_callable, route_map: dict):
        self.workflow.add_conditional_edges(source, condition_callable, route_map)
        return self

    def compile(self):
        """Compiles the graph and attaches the standard memory saver."""
        checkpointer = CheckpointManager.get_saver()
        return self.workflow.compile(checkpointer=checkpointer)
