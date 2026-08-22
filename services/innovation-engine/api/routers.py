from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from services.innovation_engine.domain.project_models import ProjectRequest, ProjectState
from services.innovation_engine.application.innovation_service import InnovationApplicationService
from services.innovation_engine.repositories.project_repo import InMemoryProjectRepository
from services.innovation_engine.orchestrator.events import event_streamer

router = APIRouter(prefix="/api/v1", tags=["Innovation Engine"])

# Singleton repo
_repo = InMemoryProjectRepository()

def get_innovation_service():
    return InnovationApplicationService(_repo)

@router.post("/projects", response_model=ProjectState)
async def start_project(
    request: ProjectRequest,
    service: InnovationApplicationService = Depends(get_innovation_service)
):
    """
    Kicks off the real Master Innovation Pipeline using LangGraph asynchronously.
    """
    return await service.start_invention_project(request)

@router.get("/projects/{project_id}/status")
async def get_project_status(
    project_id: str,
    service: InnovationApplicationService = Depends(get_innovation_service)
):
    """
    Gets the current project completion status.
    """
    return await service.get_project_status(project_id)

@router.get("/projects/{project_id}/events")
async def stream_project_events(project_id: str):
    """
    Server-Sent Events (SSE) endpoint to stream real-time LangGraph execution events.
    """
    return StreamingResponse(
        event_streamer.subscribe(project_id),
        media_type="text/event-stream"
    )

@router.post("/workflow/{project_id}/resume")
async def resume_workflow(project_id: str):
    """Stub for resuming paused workflow."""
    return {"status": "Not implemented"}

@router.post("/workflow/{project_id}/cancel")
async def cancel_workflow(project_id: str):
    """Stub for cancelling workflow."""
    return {"status": "Not implemented"}
