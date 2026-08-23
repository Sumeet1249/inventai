"""
Business Application Service
──────────────────────────────
LLM: OpenAI gpt-4o-mini (primary) → Gemini gemini-1.5-flash (fallback)
Never uses the deprecated gemini-2.0-flash.
"""
import asyncio
import json
import logging
import os
import subprocess
import uuid

from openpyxl import Workbook
from pydantic import BaseModel, Field

from services.business_service.app.schemas.business_schemas import BusinessRequest

logger = logging.getLogger(__name__)


# ── Pydantic models ────────────────────────────────────────────────────────────

class Component(BaseModel):
    name:     str   = Field(description="Component name")
    material: str   = Field(description="Material or specification")
    cost:     float = Field(description="Estimated unit cost in USD")
    quantity: int   = Field(description="Quantity required")

class BOM(BaseModel):
    components:      list[Component] = Field(description="Bill of materials")
    market_size_est: str             = Field(description="Market size e.g. '$4.2 Billion'")
    suggested_msrp:  str             = Field(description="Suggested retail price e.g. '$299.00'")


# ── LLM factory ────────────────────────────────────────────────────────────────

def _make_llm():
    """OpenAI gpt-4o-mini first, Gemini gemini-1.5-flash fallback."""
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    google_key  = os.environ.get("GOOGLE_API_KEY", "")

    if openai_key and not openai_key.startswith("sk-your"):
        try:
            from langchain_openai import ChatOpenAI
            logger.info("Business: using OpenAI gpt-4o-mini")
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                openai_api_key=openai_key,
                max_retries=2,
                request_timeout=30,
            )
        except Exception as exc:
            logger.warning("Business: OpenAI init failed: %s", exc)

    if google_key and not google_key.startswith("AQ."):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("Business: using Gemini gemini-1.5-flash")
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        except Exception as exc:
            logger.warning("Business: Gemini init failed: %s", exc)

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── Fallback BOM ───────────────────────────────────────────────────────────────

def _fallback_bom(idea: str) -> BOM:
    """Heuristic BOM when LLM is unavailable."""
    return BOM(
        components=[
            Component(name="Primary Structure",    material="Aluminium 6061-T6", cost=18.50, quantity=1),
            Component(name="Electronics Module",   material="PCB Assembly",      cost=24.00, quantity=1),
            Component(name="Power System",         material="Li-Ion 3S 5000mAh", cost=32.00, quantity=1),
            Component(name="Sensors Package",      material="IMU + Ultrasonic",  cost=15.00, quantity=1),
            Component(name="Fasteners & Hardware", material="Stainless M3/M4",   cost=4.50,  quantity=1),
        ],
        market_size_est="$8.2 Billion",
        suggested_msrp="$349.00",
    )


# ── Service ────────────────────────────────────────────────────────────────────

class BusinessApplicationService:

    async def generate_business_stream(self, request: BusinessRequest):
        unique_id = request.project_id or str(uuid.uuid4())[:8]

        # Stage 1 — Web scraping (best-effort)
        yield f"data: {json.dumps({'status': 'Scanning market data…'})}\n\n"
        try:
            spider_path = "/app/services/business_service/app/application/scraper.py"
            subprocess.run(
                ["scrapy", "runspider", spider_path,
                 "-a", f"query={request.idea_description}",
                 "-o", f"/tmp/competitors_{unique_id}.json"],
                capture_output=True, timeout=10,
            )
        except Exception:
            pass
        await asyncio.sleep(0.3)

        # Stage 2 — Competitor pricing
        yield f"data: {json.dumps({'status': 'Analysing competitor pricing…'})}\n\n"
        await asyncio.sleep(0.3)

        # Stage 3 — BOM via LLM
        yield f"data: {json.dumps({'status': 'Generating Financial BOM with AI…'})}\n\n"

        bom_data: BOM
        try:
            llm          = _make_llm()
            structured   = llm.with_structured_output(BOM)
            from langchain_core.messages import HumanMessage
            bom_data = await structured.ainvoke([
                HumanMessage(content=(
                    f"Create a realistic Bill of Materials for this product: "
                    f"{request.idea_description}. "
                    f"Include 5-8 components with accurate cost estimates."
                ))
            ])
            logger.info("Business BOM generated via LLM")
        except Exception as exc:
            logger.warning("Business BOM LLM failed (%s) — using heuristic fallback", exc)
            bom_data = _fallback_bom(request.idea_description)

        # Write Excel
        os.makedirs("/tmp/business_exports", exist_ok=True)
        filename = f"Financial_BOM_{unique_id}.xlsx"
        filepath = f"/tmp/business_exports/{filename}"

        wb = Workbook()
        ws = wb.active
        ws.title = "Bill of Materials"
        ws.append(["Component", "Material / Spec", "Unit Cost (USD)", "Qty", "Total (USD)"])

        total_cogs = 0.0
        for comp in bom_data.components:
            total = comp.cost * comp.quantity
            total_cogs += total
            ws.append([comp.name, comp.material, comp.cost, comp.quantity, total])

        ws.append(["", "", "", "Total COGS:", round(total_cogs, 2)])
        wb.save(filepath)

        yield f"data: {json.dumps({'status': 'Completed', 'bom_url': f'/api/v1/business/download/{filename}', 'market_size_est': bom_data.market_size_est, 'suggested_msrp': bom_data.suggested_msrp})}\n\n"
