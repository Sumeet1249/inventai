from langchain_core.messages import SystemMessage
from services.ai_agent_service.shared.state import AgentState

def research_agent_node(state: AgentState):
    # This node will interact with LlamaIndex and ChromaDB
    insights = [{"paper_doi": "10.1234/5678", "findings": "Solid state batteries require ceramic electrolytes."}]
    
    return {
        "research_insights": insights,
        "messages": [SystemMessage(content="Research Agent completed semantic literature review.")]
    }
