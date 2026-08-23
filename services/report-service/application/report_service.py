from fastapi import FastAPI
from services.report_service.domain.report_models import ReportRequest, ReportMetadata
from packages.ai_core.memory.memory_manager import MemoryManager
from services.report_service.composition.artifact_collector import ArtifactCollector
from services.report_service.composition.document_composer import DocumentComposer
from services.report_service.exporters.pdf import PDFExporter
from services.report_service.exporters.docx import DOCXExporter
from services.report_service.exporters.packager import ReportPackager
import asyncio
import json
import uuid

class ReportApplicationService:
    """
    Business use case orchestrator for Report Generation.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    async def generate_report_stream(self, request: ReportRequest):
        """
        Triggers the AI composition and yields SSE events.
        """
        unique_id = request.project_id or str(uuid.uuid4())[:8]
        
        # 1. Collect Artifacts
        yield f"data: {json.dumps({'status': 'Collecting Workflow Artifacts'})}\n\n"
        await asyncio.sleep(0.5)
        artifacts = ArtifactCollector.collect(unique_id)
        
        # 2. Document Composition
        yield f"data: {json.dumps({'status': 'Drafting Patent & Engineering Reports'})}\n\n"
        await asyncio.sleep(0.5)
        patent_md = DocumentComposer.compose_patent_draft(artifacts)
        engineering_md = DocumentComposer.compose_engineering_report(artifacts)
        
        # 3. Exporters
        yield f"data: {json.dumps({'status': 'Exporting to PDF and DOCX'})}\n\n"
        await asyncio.sleep(0.5)
        
        pdf_path = f"/tmp/report_exports/Patent_Draft_{unique_id}.pdf"
        docx_path = f"/tmp/report_exports/Engineering_Report_{unique_id}.docx"
        
        PDFExporter.export(patent_md, pdf_path)
        DOCXExporter.export(engineering_md, docx_path)
        
        # 4. Packaging
        yield f"data: {json.dumps({'status': 'Packaging Final ZIP Deliverable'})}\n\n"
        await asyncio.sleep(0.5)
        
        zip_path = f"/tmp/report_exports/InventAI_Package_{unique_id}.zip"
        files_to_zip = [
            pdf_path,
            docx_path,
            artifacts["cad_assets"].get("step"),
            artifacts["cad_assets"].get("stl"),
            artifacts["physics_assets"].get("heatmap")
        ]
        
        ReportPackager.package(unique_id, files_to_zip, zip_path)
        
        yield f"data: {json.dumps({'status': 'Completed', 'download_url': f'/api/v1/reports/download/InventAI_Package_{unique_id}.zip'})}\n\n"

# Create and configure FastAPI app
app = FastAPI(
    title="InventAI Report Service",
    description="Patent drafting and engineering report composition",
    version="1.0.0"
)

# Lazy import to avoid circular dependencies
from services.report_service.api.routers import router
app.include_router(router)
