from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse
from services.business_service.app.schemas.business_schemas import BusinessRequest
from services.business_service.app.application.business_service import BusinessApplicationService
import os

router = APIRouter(prefix="/api/v1/business", tags=["Business Intelligence"])

def get_business_service():
    return BusinessApplicationService()

@router.post("/generate")
async def generate_business_plan(
    request: BusinessRequest,
    service: BusinessApplicationService = Depends(get_business_service)
):
    """
    Generates Market Sizing and Financial BOM. Streams SSE progress.
    """
    return StreamingResponse(
        service.generate_business_stream(request),
        media_type="text/event-stream"
    )

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = f"/tmp/business_exports/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}
