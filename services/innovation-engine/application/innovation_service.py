from fastapi import FastAPI
from services.innovation_engine.domain.project_models import ProjectState, ProjectRequest
from services.innovation_engine.repositories.project_repo import InMemoryProjectRepository
from services.innovation_engine.orchestrator.graph import build_innovation_graph
from services.innovation_engine.orchestrator.state import InnovationWorkflowState
from services.innovation_engine.orchestrator.events import event_streamer
import asyncio

class InnovationApplicationService:
    def __init__(self, repo: InMemoryProjectRepository):
        self.repo = repo
        self.workflow = build_innovation_graph()

    async def _execute_workflow_async(self, project: ProjectState, initial_state: InnovationWorkflowState):
        """Runs the LangGraph workflow in the background and streams events."""
        try:
            await event_streamer.publish(project.id, "WorkflowStarted", {"project_id": project.id})
            
            # Use LangGraph's streaming API
            async for event in self.workflow.astream(initial_state, stream_mode="values"):
                # `event` contains the entire state dict
                current_step = event.get("current_step", "Planner")
                completed = event.get("completed_steps", [])
                
                await event_streamer.publish(project.id, "NodeCompleted", {
                    "node": current_step,
                    "completed_steps": completed,
                    "artifacts": event.get("artifacts", {})
                })
                
            await event_streamer.publish(project.id, "WorkflowCompleted", {"project_id": project.id})
            
            # Final DB Update
            project.status = "Completed"
            await self.repo.update(project)
            
        except Exception as e:
            await event_streamer.publish(project.id, "WorkflowFailed", {"error": str(e)})
            project.status = "Failed"
            await self.repo.update(project)

    async def start_invention_project(self, request: ProjectRequest) -> ProjectState:
        project = ProjectState(name=request.name, description=request.idea_description)
        project.status = "Orchestrating"
        await self.repo.create(project)
        
        initial_state = {
            "project_id": project.id,
            "idea": request.idea_description,
            "user_id": "system",
            "plan": [],
            "completed_steps": [],
            "artifacts": {},
            "logs": [],
            "errors": [],
            "timing": {},
            "current_step": None
        }
        
        # Fire and forget background task
        asyncio.create_task(self._execute_workflow_async(project, initial_state))
        
        return project

    async def get_project_status(self, project_id: str) -> dict:
        project = await self.repo.get_by_id(project_id)
        if not project:
            return {"status": "NotFound"}
        return {"status": project.status}

# Create and configure FastAPI app
app = FastAPI(
    title="InventAI Innovation Engine",
    description="Master orchestrator for autonomous engineering",
    version="1.0.0"
)

@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "service": "innovation-engine"}

# Lazy import to avoid circular dependencies
from services.innovation_engine.api.routers import router
app.include_router(router)
