from fastapi import APIRouter, Depends
from services.report_service.domain.report_models import ReportRequest, ReportMetadata
from services.report_service.application.report_service import ReportApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

router = APIRouter(prefix="/api/v1/reports", tags=["Report Generation Engine"])

class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

def get_report_service():
    memory_manager = MemoryManager(MockMemoryProvider())
    return ReportApplicationService(memory_manager)

from fastapi.responses import FileResponse, StreamingResponse
import os

@router.post("/generate")
async def generate_report(
    request: ReportRequest,
    service: ReportApplicationService = Depends(get_report_service)
):
    """
    Triggers the AI composition pipeline and streams SSE progress.
    """
    return StreamingResponse(
        service.generate_report_stream(request),
        media_type="text/event-stream"
    )

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/tmp/report_exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

