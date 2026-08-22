from fastapi import APIRouter, Depends
from services.physics_service.schemas.physics_schemas import SimulationRequest
from services.physics_service.application.physics_service import PhysicsApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

router = APIRouter(prefix="/api/v1/physics", tags=["Physics Intelligence"])

class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

def get_physics_service():
    memory_manager = MemoryManager(MockMemoryProvider())
    return PhysicsApplicationService(memory_manager)

from fastapi.responses import FileResponse, StreamingResponse
import os

@router.post("/simulate")
async def execute_simulation(
    request: SimulationRequest,
    service: PhysicsApplicationService = Depends(get_physics_service)
):
    """
    Triggers the PINN physics engine and streams back Server-Sent Events (SSE) detailing the progress.
    """
    return StreamingResponse(
        service.run_simulation_stream(request),
        media_type="text/event-stream"
    )

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/tmp/physics_exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

