from langgraph.graph import StateGraph, END
from services.innovation_engine.orchestrator.state import InnovationWorkflowState
from services.innovation_engine.orchestrator.planner import PlannerAgent
from services.innovation_engine.orchestrator.executor import (
    patent_node, research_node, kg_node, cad_node, physics_node, business_node, report_node, reviewer_node
)

def route_next_step(state: InnovationWorkflowState) -> str:
    """Router logic to pick the next step based on the plan."""
    plan = state.get("plan", [])
    completed = state.get("completed_steps", [])
    
    for step in plan:
        if step not in completed:
            return step
    return END

def build_innovation_graph():
    """Builds the Enterprise LangGraph."""
    workflow = StateGraph(InnovationWorkflowState)
    
    # Add Nodes
    planner = PlannerAgent()
    workflow.add_node("Planner", planner.execute)
    
    # Domain Nodes
    workflow.add_node("Patent", patent_node.execute)
    workflow.add_node("Research", research_node.execute)
    workflow.add_node("KnowledgeGraph", kg_node.execute)
    workflow.add_node("CAD", cad_node.execute)
    workflow.add_node("Physics", physics_node.execute)
    workflow.add_node("Business", business_node.execute)
    workflow.add_node("Report", report_node.execute)
    workflow.add_node("Reviewer", reviewer_node.execute)
    
    # Entry Point
    workflow.set_entry_point("Planner")
    
    # Edge Router
    nodes = ["Patent", "Research", "KnowledgeGraph", "CAD", "Physics", "Business", "Report", "Reviewer"]
    workflow.add_conditional_edges(
        "Planner",
        route_next_step,
        {n: n for n in nodes} | {END: END}
    )
    
    for n in nodes:
        workflow.add_conditional_edges(
            n,
            route_next_step,
            {nxt: nxt for nxt in nodes} | {END: END}
        )
        
    # We could add checkpointer here (e.g. MemorySaver or SqliteSaver)
    return workflow.compile()
