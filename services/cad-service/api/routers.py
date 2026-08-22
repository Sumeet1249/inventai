from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
import os

from services.cad_service.schemas.cad_schemas import CADGenerationRequest
from services.cad_service.application.cad_service import CADApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

router = APIRouter(prefix="/api/v1/cad", tags=["CAD Intelligence"])

_EXPORT_DIR = "/tmp/cad_exports"

# Mock memory provider for DI
class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

def get_cad_service():
    memory_manager = MemoryManager(MockMemoryProvider())
    return CADApplicationService(memory_manager)


@router.post("/generate")
async def generate_cad_model(
    request: CADGenerationRequest,
    service: CADApplicationService = Depends(get_cad_service)
):
    """
    Generates a CAD model from a natural-language description via CAD-Coder.
    Streams Server-Sent Events (SSE) showing live pipeline progress.
    """
    return StreamingResponse(
        service.generate_model_stream(request),
        media_type="text/event-stream"
    )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Serve a generated export file (GLTF / STEP / STL)."""
    # Reject path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")

    file_path = os.path.join(_EXPORT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {filename}")

    return FileResponse(file_path)


@router.get("/{id}/preview")
async def get_cad_preview(id: str):
    return {"url": f"/api/v1/cad/download/{id}.gltf"}


@router.get("/{id}/exports")
async def get_cad_exports(id: str):
    return {
        "step":  f"/api/v1/cad/download/{id}.step",
        "gltf":  f"/api/v1/cad/download/{id}.gltf",
        "stl":   f"/api/v1/cad/download/{id}.stl",
    }


@router.get("/{id}")
async def get_cad_metadata(id: str):
    return {"id": id, "status": "completed"}

