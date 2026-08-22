from langchain_core.messages import SystemMessage
from services.ai_agent_service.shared.state import AgentState

def patent_agent_node(state: AgentState):
    # This node will interact with Neo4j and PQAI
    # For now, we simulate the interaction
    insights = [{"patent_id": "US12345", "relevance": 0.95, "summary": "Similar technology found."}]
    
    return {
        "patent_insights": insights,
        "messages": [SystemMessage(content="Patent Agent completed prior art search.")]
    }
