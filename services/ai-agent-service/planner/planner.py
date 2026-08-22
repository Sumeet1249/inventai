from langchain_core.messages import HumanMessage, SystemMessage
from packages.ai.llm import get_llm
from services.ai_agent_service.shared.state import AgentState

def planner_node(state: AgentState):
    llm = get_llm()
    messages = [
        SystemMessage(content="You are the lead planner for InventAI. Break down the user's request into a series of actionable steps for the specialized agents (Patent, Research, CAD). Return ONLY a JSON list of strings."),
        HumanMessage(content=state["user_request"])
    ]
    response = llm.invoke(messages)
    
    # In production, parse the JSON response
    # For now, we mock the parsed response
    plan = ["Query PQAI for prior art", "Search LlamaIndex for research papers"]
    
    return {"plan": plan, "messages": [SystemMessage(content=f"Planner generated {len(plan)} steps.")]}
