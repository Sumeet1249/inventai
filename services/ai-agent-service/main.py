from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="InventAI AI Agent Service",
    description="LangGraph-based multi-agent orchestration (planner → patent → research)",
    version="1.0.0",
)


class AgentRequest(BaseModel):
    project_id: str
    user_request: str


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai-agent-service"}


@app.post("/api/v1/agent/run")
async def run_agent(request: AgentRequest):
    """
    Runs the LangGraph InventCore multi-agent pipeline:
    Planner → PatentAgent → ResearchAgent
    """
    from services.ai_agent_service.orchestrator.graph import inventcore_app
    from services.ai_agent_service.shared.state import AgentState

    initial_state: AgentState = {
        "messages": [],
        "project_id": request.project_id,
        "user_request": request.user_request,
        "plan": [],
        "patent_insights": [],
        "research_insights": [],
        "cad_parameters": {},
        "physics_results": {},
        "validation_status": "pending",
        "final_report_path": "",
    }

    result = await inventcore_app.ainvoke(initial_state)
    return {"status": "completed", "result": result}
