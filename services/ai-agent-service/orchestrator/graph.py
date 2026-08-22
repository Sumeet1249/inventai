from langgraph.graph import StateGraph, END
from services.ai_agent_service.shared.state import AgentState
from services.ai_agent_service.planner.planner import planner_node
from services.ai_agent_service.patent_agent.patent import patent_agent_node
from services.ai_agent_service.research_agent.research import research_agent_node

def create_inventcore_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("patent_agent", patent_agent_node)
    workflow.add_node("research_agent", research_agent_node)
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Add edges
    workflow.add_edge("planner", "patent_agent")
    workflow.add_edge("patent_agent", "research_agent")
    workflow.add_edge("research_agent", END)
    
    return workflow.compile()

# The compiled graph
inventcore_app = create_inventcore_graph()
