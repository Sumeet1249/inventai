from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from services.patent_service.tools.patent_search import PatentSearchTool, PatentSearchInput
from services.patent_service.tools.novelty_tool import NoveltyAnalysisTool, NoveltyInput
from services.patent_service.tools.epo_search import EpoSearchTool, EpoSearchInput
from services.patent_service.tools.wipo_search import WipoSearchTool, WipoSearchInput
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tools.context import ToolContext

def build_patent_analysis_workflow(memory_manager: MemoryManager):
    """
    Builds the LangGraph orchestration for Patent Analysis.
    Performs RAG Pipeline: Search Prior Art -> Analyze Novelty -> Return Result
    """
    builder = WorkflowBuilder()

    # 1. Instantiate Tools
    search_tool = PatentSearchTool()
    epo_tool = EpoSearchTool()
    wipo_tool = WipoSearchTool()
    novelty_tool = NoveltyAnalysisTool()

    # 3. Define Nodes
    async def search_node(state: WorkflowState):
        idea = state.get("input_data", {}).get("idea", "")
        context = ToolContext(
            session_id=state.get("session_id", "default"),
            workflow_id=state.get("workflow_id", "default"),
            agent_id="patent_agent"
        )
        # Execute the real search tools
        uspto_result = await search_tool.execute(PatentSearchInput(query=idea, top_k=3), context)
        epo_result = await epo_tool.execute(EpoSearchInput(query=idea, top_k=2), context)
        wipo_result = await wipo_tool.execute(WipoSearchInput(query=idea, top_k=2), context)
        
        all_results = uspto_result.results + epo_result.results + wipo_result.results
        
        state["metadata"]["prior_art"] = all_results
        return {"metadata": state["metadata"]}

    async def analysis_node(state: WorkflowState):
        idea = state.get("input_data", {}).get("idea", "")
        prior_art = state.get("metadata", {}).get("prior_art", [])
        
        context = ToolContext(
            session_id=state.get("session_id", "default"),
            workflow_id=state.get("workflow_id", "default"),
            agent_id="patent_agent"
        )
        
        # Execute the RAG Novelty Tool
        novelty_result = await novelty_tool.execute(NoveltyInput(idea=idea, prior_art=prior_art), context)
        
        state["output_data"] = {
            "novelty_score": novelty_result.novelty_score,
            "gaps_found": novelty_result.gaps_found,
            "rejections": novelty_result.rejections,
            "summary": novelty_result.summary,
            "prior_art": prior_art
        }
        return {"output_data": state["output_data"]}

    # 4. Construct Graph
    builder.workflow.add_node("search", search_node)
    builder.workflow.add_node("analysis", analysis_node)

    builder.workflow.set_entry_point("search")
    builder.workflow.add_edge("search", "analysis")
    builder.workflow.set_finish_point("analysis")

    return builder.compile()
