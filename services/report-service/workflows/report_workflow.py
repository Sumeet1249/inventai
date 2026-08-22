from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from services.report_service.templates.jinja_manager import JinjaManager
from services.report_service.exporters.pdf_exporter import PDFExporter
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.memory.memory_manager import MemoryManager

def build_report_orchestration_workflow(memory_manager: MemoryManager):
    """
    Builds the LangGraph orchestration for generating professional reports.
    """
    builder = WorkflowBuilder()

    context = AgentContext(agent_id="report_orchestrator", role="writer")
    planner = AgentFactory.create_agent("planner", context, memory_manager)

    async def draft_prose(state: WorkflowState):
        # AI synthesizes the JSON data into a coherent Markdown draft
        project_data = state.input_data.get("project_data", {})
        markdown = JinjaManager.render_markdown("corporate_theme", project_data)
        state.metadata["markdown_draft"] = markdown
        return {"metadata": state.metadata}

    async def export_document(state: WorkflowState):
        # Converts the Markdown to a physical file
        draft = state.metadata.get("markdown_draft")
        file_path = PDFExporter.export(draft, f"report_{state.workflow_id}")
        state.output_data = {"download_url": f"https://cdn.inventai.com/{file_path}"}
        return {"output_data": state.output_data}

    builder.add_node("draft", draft_prose)
    builder.add_node("export", export_document)

    builder.set_entry_point("draft")
    builder.add_edge("draft", "export")
    builder.set_finish_point("export")

    return builder.compile()
