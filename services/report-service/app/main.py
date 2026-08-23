"""
Report Generation Service — FastAPI
────────────────────────────────────
Compiles all multi-agent outputs into publication-ready PDF and DOCX engineering packages.

Endpoints:
  POST /api/v1/reports/generate
    Body: ReportRequest with all agent outputs
    Returns: ReportResponse with PDF/DOCX download URLs

  GET /api/v1/reports/{filename}
    Returns: File download

  GET /health
    Returns: Service health status
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.schemas import (
    ReportRequest,
    ReportResponse,
    HealthResponse,
)
from app.report_generator import (
    generate_html_report,
    render_html_to_pdf,
    create_docx_report,
    save_report_files,
    EXPORT_DIR,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InventAI Report Generation Service",
    description="Autonomous Multi-Agent Engineering Report Generator (PDF + DOCX)",
    version="1.0.0",
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache for generation status
_generation_cache: dict[str, dict] = {}


@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint"""
    return HealthResponse(
        status="ok",
        service="report-service",
        version="1.0.0",
    )


@app.post("/api/v1/reports/generate")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks) -> ReportResponse:
    """
    Generate engineering report in PDF and DOCX formats.
    
    Expects:
      - project_id: unique project identifier
      - project_title: display name
      - agent_outputs: outputs from Patent, Physics, CAD, PCB, Business agents
    
    Returns:
      - report_urls: download URLs for PDF and DOCX
      - generation_time_seconds: total generation time
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating report for project: {request.project_id}")
        
        # Update cache with "in progress" status
        _generation_cache[request.project_id] = {
            "status": "generating",
            "start_time": start_time,
        }
        
        # ═════════════ Step 1: Generate HTML ═════════════
        logger.info("Step 1/3: Rendering HTML template...")
        html_content = generate_html_report(request)
        logger.info("✓ HTML template rendered")
        
        # ═════════════ Step 2: Generate PDF ═════════════
        logger.info("Step 2/3: Generating PDF...")
        pdf_bytes = render_html_to_pdf(html_content, request.project_id)
        if not pdf_bytes:
            logger.warning("PDF generation failed, continuing with DOCX only")
        else:
            logger.info(f"✓ PDF generated ({len(pdf_bytes) / 1024:.1f} KB)")
        
        # ═════════════ Step 3: Generate DOCX ═════════════
        logger.info("Step 3/3: Generating DOCX...")
        docx_bytes = create_docx_report(request)
        if not docx_bytes:
            logger.warning("DOCX generation failed, continuing with PDF only")
        else:
            logger.info(f"✓ DOCX generated ({len(docx_bytes) / 1024:.1f} KB)")
        
        # ═════════════ Step 4: Save files ═════════════
        logger.info("Step 4/3: Saving files...")
        report_urls = save_report_files(request.project_id, pdf_bytes, docx_bytes)
        
        # Calculate generation time
        elapsed = time.time() - start_time
        logger.info(f"✓ Report generation completed in {elapsed:.2f}s")
        
        # Update cache with success
        _generation_cache[request.project_id] = {
            "status": "completed",
            "start_time": start_time,
            "elapsed": elapsed,
            "urls": report_urls,
        }
        
        # Return response
        response = ReportResponse(
            status="success",
            project_id=request.project_id,
            report_urls=report_urls,
            generation_time_seconds=elapsed,
            message=f"Report generated in {elapsed:.2f} seconds",
        )
        
        logger.info(f"Report response: {response.model_dump_json()}")
        return response
    
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Report generation failed: {e}", exc_info=True)
        
        _generation_cache[request.project_id] = {
            "status": "error",
            "start_time": start_time,
            "elapsed": elapsed,
            "error": str(e),
        }
        
        raise HTTPException(
            status_code=500,
            detail=f"Report generation failed: {str(e)}"
        )


@app.get("/api/v1/reports/{filename}")
async def download_report(filename: str):
    """
    Download a generated report file (PDF or DOCX).
    
    Security: Validates filename to prevent path traversal.
    """
    # Validate filename
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = EXPORT_DIR / filename
    
    if not file_path.exists():
        logger.warning(f"Report file not found: {file_path}")
        raise HTTPException(status_code=404, detail="Report file not found")
    
    logger.info(f"Downloading report: {filename}")
    
    # Determine media type
    if filename.endswith('.pdf'):
        media_type = "application/pdf"
    elif filename.endswith('.docx'):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        media_type = "application/octet-stream"
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type,
    )


@app.get("/api/v1/reports/status/{project_id}")
async def report_status(project_id: str):
    """
    Check the generation status of a report.
    
    Returns:
      - status: "queued", "generating", "completed", "error"
      - elapsed: seconds elapsed
      - urls: download URLs (if completed)
      - error: error message (if failed)
    """
    cache_entry = _generation_cache.get(project_id)
    
    if not cache_entry:
        return {
            "status": "not_found",
            "project_id": project_id,
        }
    
    return {
        "project_id": project_id,
        **cache_entry,
    }


@app.delete("/api/v1/reports/{project_id}")
async def delete_report(project_id: str):
    """
    Delete generated report files for a project.
    """
    try:
        pdf_path = EXPORT_DIR / f"{project_id}_Engineering_Report.pdf"
        docx_path = EXPORT_DIR / f"{project_id}_Engineering_Report.docx"
        
        deleted = []
        
        if pdf_path.exists():
            pdf_path.unlink()
            deleted.append("pdf")
            logger.info(f"Deleted PDF: {pdf_path}")
        
        if docx_path.exists():
            docx_path.unlink()
            deleted.append("docx")
            logger.info(f"Deleted DOCX: {docx_path}")
        
        return {
            "status": "success",
            "project_id": project_id,
            "deleted": deleted,
        }
    
    except Exception as e:
        logger.error(f"Failed to delete reports: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.get("/api/v1/reports")
async def list_reports():
    """
    List all generated reports.
    """
    try:
        reports = []
        for file_path in EXPORT_DIR.glob("*_Engineering_Report.*"):
            reports.append({
                "filename": file_path.name,
                "size_bytes": file_path.stat().st_size,
                "created": file_path.stat().st_mtime,
            })
        
        return {
            "status": "success",
            "count": len(reports),
            "reports": reports,
        }
    
    except Exception as e:
        logger.error(f"Failed to list reports: {e}")
        raise HTTPException(status_code=500, detail=f"Listing failed: {str(e)}")


@app.post("/api/v1/reports/test")
async def test_report_generation():
    """
    Test endpoint: Generate a sample report with mock data.
    Useful for verifying the service is working correctly.
    """
    from app.schemas import (
        PatentOutput,
        PhysicsOutput,
        CADOutput,
        PCBOutput,
        BOMItem,
        BusinessOutput,
        AgentOutputs,
    )
    
    test_request = ReportRequest(
        project_id="test_drone_450mm",
        project_title="Foldable Bridge Inspection Drone",
        author="InventAI Test Suite",
        company_name="InventAI",
        confidentiality_level="CONFIDENTIAL",
        agent_outputs=AgentOutputs(
            patent=PatentOutput(
                novelty_score=88.5,
                fto_status="CLEARED",
                white_space_summary="Unclaimed technological gap identified in combining a 450mm folding CFRP quadcopter frame with 200kHz concrete-crack ultrasonic transducers.",
                claims_draft=[
                    "A modular foldable drone frame comprising carbon fiber reinforced polymer (CFRP) composite structure with magnetic locking mechanisms.",
                    "The system of claim 1, further comprising integrated ultrasonic transducer array for non-destructive testing applications.",
                ]
            ),
            physics=PhysicsOutput(
                validation_status="PASS",
                safety_factor=2.80,
                max_stress_mpa=214.28,
                yield_strength_mpa=600.0,
                simulation_summary="Finite element analysis validates structural integrity under 10g acceleration loads with 2.8x safety factor. Peak stress concentration at motor mounts."
            ),
            cad=CADOutput(
                format="STEP / B-Rep",
                dimensions="450mm diagonal motor span (180mm folded)",
                assembly_summary="Modular frame assembly with quick-disconnect battery and payload bay. Tool-free folding mechanism with redundant locking pins."
            ),
            pcb=PCBOutput(
                board_specs="Dual-Layer Edge-AI Flight Controller (85mm x 60mm). NVIDIA Jetson Orin NX compute module with 4x Motor ESCs.",
                spice_status="PASS",
                schematic_summary="Power distribution: 6S LiPo battery → 5V main rail (5.02V regulated, ±2% tolerance). Motor PWM outputs: 50kHz carrier frequency. All bypass capacitors optimized for 1MHz switching transients."
            ),
            business=BusinessOutput(
                total_cogs_usd=5200.00,
                target_msrp_usd=12000.00,
                gross_margin_percent=56.67,
                bom_table=[
                    BOMItem(item="CFRP Frame Kit", qty=1, cost=450.00, supplier="SZ Composites"),
                    BOMItem(item="NVIDIA Jetson Orin NX", qty=1, cost=599.00, supplier="NVIDIA Direct"),
                    BOMItem(item="Velodyne VLP-16 LiDAR", qty=1, cost=2800.00, supplier="Velodyne"),
                    BOMItem(item="T-Motor U8 Pro ESC (4x)", qty=4, cost=150.00, supplier="T-Motor"),
                    BOMItem(item="Flight Battery 6S 5000mAh", qty=2, cost=120.00, supplier="DJI"),
                    BOMItem(item="Wiring & Connectors", qty=1, cost=81.00, supplier="Local"),
                ],
                financial_summary="Highly profitable product with 56.7% gross margin. Jetson Orin edge processing enables autonomous mission planning. LiDAR adds premium positioning capability. Target 500+ units/year with 18-month path to profitability."
            )
        )
    )
    
    return await generate_report(test_request, BackgroundTasks())


# ═════════════════════════ STARTUP / SHUTDOWN ═════════════════════════

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("InventAI Report Generation Service starting up...")
    logger.info(f"Export directory: {EXPORT_DIR}")
    logger.info("Report service ready to accept requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("InventAI Report Generation Service shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
