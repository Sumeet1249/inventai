import pytest
from services.report_service.domain.report_models import ReportRequest
from services.report_service.application.report_service import ReportApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tests.test_agent_lifecycle import MockMemoryProvider

@pytest.mark.asyncio
async def test_report_workflow_generation():
    manager = MemoryManager(MockMemoryProvider())
    service = ReportApplicationService(manager)
    
    req = ReportRequest(
        project_id="proj_123", 
        report_type="patent_draft",
        project_data={"name": "Flying Car", "description": "A car that flies."}
    )
    
    # Execute the LangGraph workflow end-to-end
    result = await service.generate_report(req)
    
    assert result.status == "Completed"
    assert "cdn.inventai.com" in result.download_url
