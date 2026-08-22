from fastapi import APIRouter, Depends
from services.cad_service.schemas.cad_schemas import CADGenerationRequest
from services.cad_service.application.cad_service import CADApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

router = APIRouter(prefix="/api/v1/cad", tags=["CAD Intelligence"])

# Mock memory provider for DI
class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

def get_cad_service():
    memory_manager = MemoryManager(MockMemoryProvider())
    return CADApplicationService(memory_manager)

from fastapi.responses import FileResponse, StreamingResponse
import os

@router.post("/generate")
async def generate_cad_model(
    request: CADGenerationRequest,
    service: CADApplicationService = Depends(get_cad_service)
):
    """
    Triggers the LangGraph AI Workflow to parametrically generate a CAD model
    and streams back Server-Sent Events (SSE) detailing the progress.
    """
    return StreamingResponse(
        service.generate_model_stream(request),
        media_type="text/event-stream"
    )


@router.get("/{id}")
async def get_cad_metadata(id: str):
    return {"id": id, "status": "completed"}

@router.get("/{id}/preview")
async def get_cad_preview(id: str):
    return {"url": f"/api/v1/cad/download/{id}.gltf"}

@router.get("/{id}/exports")
async def get_cad_exports(id: str):
    return {
        "step": f"/api/v1/cad/download/{id}.step",
        "gltf": f"/api/v1/cad/download/{id}.gltf"
    }

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/tmp/cad_exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

