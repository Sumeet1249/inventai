"""
Circuit Service — FastAPI
─────────────────────────
POST /api/v1/circuit/generate
  Body: { "project_id": str, "cad_spec": {...} }
  Returns: SSE stream with circuit data

GET /api/v1/circuit/schematic/{project_id}
  Returns: SVG schematic as image/svg+xml
"""

from __future__ import annotations
import asyncio
import json
import logging
import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel
from typing import Any

from app.circuit_generator import generate_circuit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="InventAI Circuit Service",
    description="CAD → Circuit Design: electronics agent + SVG schematic + BOM",
    version="1.0.0",
)

# In-memory cache: project_id → circuit result
_cache: dict[str, dict] = {}


class CircuitRequest(BaseModel):
    project_id: str
    cad_spec: dict[str, Any] = {}
    idea: str = ""


@app.get("/health")
async def health():
    return {"status": "ok", "service": "circuit-service"}


@app.post("/api/v1/circuit/generate")
async def generate(request: CircuitRequest):
    """
    Generates circuit from CAD spec. Streams SSE progress events.
    """
    async def stream():
        yield f"data: {json.dumps({'status': 'Analysing CAD spec…'})}\n\n"
        await asyncio.sleep(0.2)

        yield f"data: {json.dumps({'status': 'Electronics agent: extracting power requirements…'})}\n\n"

        try:
            result = await generate_circuit(request.cad_spec or {"component_type": "drone_frame"})
            _cache[request.project_id] = result

            yield f"data: {json.dumps({'status': 'SVG schematic generated'})}\n\n"
            await asyncio.sleep(0.1)

            # Final payload — omit SVG from SSE (too large), send everything else
            payload = {
                "status":      "Completed",
                "project_id":  request.project_id,
                "bom":         result["bom"],
                "bom_total":   result["bom_total"],
                "power_rails": result["power_rails"],
                "elec_spec":   result["elec_spec"],
                "schematic_url": f"/api/v1/circuit/schematic/{request.project_id}",
                "component_count": len(result["bom"]),
            }
            yield f"data: {json.dumps(payload)}\n\n"

        except Exception as exc:
            logger.error("Circuit generation failed: %s", exc, exc_info=True)
            yield f"data: {json.dumps({'status': 'Error', 'error': str(exc)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.get("/api/v1/circuit/schematic/{project_id}")
async def get_schematic(project_id: str):
    """Returns the SVG schematic for a project."""
    result = _cache.get(project_id)
    if not result:
        # Generate a default schematic
        result = await generate_circuit({"component_type": "drone_frame"})
        _cache[project_id] = result

    return Response(
        content=result["svg"],
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-cache"},
    )
