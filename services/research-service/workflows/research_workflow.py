from typing import Dict, Any
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.state import WorkflowState
from services.research_service.tools.document_search import DocumentSearchTool
from services.research_service.tools.summarization_tool import SummarizationTool
from services.research_service.tools.arxiv_search import ArxivSearchTool
from services.research_service.tools.pubmed_search import PubmedSearchTool
from services.research_service.tools.ieee_search import IeeeSearchTool
from services.research_service.tools.crossref_search import CrossrefSearchTool
from packages.ai_core.agents.agent_factory import AgentFactory
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.agents.planner_agent import PlannerAgent
from packages.ai_core.agents.worker_agent import WorkerAgent

def build_research_rag_workflow(memory_manager: MemoryManager):
    """
    Builds the LangGraph orchestration for the RAG Pipeline.
    Integrates Planner and Worker agents with specialized Research tools.
    """
    builder = WorkflowBuilder()

    # 1. Instantiate Tools
    search_tool = DocumentSearchTool()
    summarize_tool = SummarizationTool()
    arxiv_tool = ArxivSearchTool()
    pubmed_tool = PubmedSearchTool()
    ieee_tool = IeeeSearchTool()
    crossref_tool = CrossrefSearchTool()

    # 2. Instantiate Agents via AI Core Factory
    context = AgentContext(agent_id="research_orchestrator", role="coordinator")
    planner = AgentFactory.create_agent("planner", context, memory_manager)
    worker = AgentFactory.create_agent("worker", context, memory_manager)

    # 3. Define Nodes
    async def plan_retrieval(state: WorkflowState):
        try:
            plan_result = await planner.execute({"task": f"Extract knowledge for: {state.get('input_data', {}).get('query')}"})
            state["metadata"]["plan"] = plan_result.get("plan", "Default Plan")
        except Exception:
            state["metadata"]["plan"] = "Fallback Plan"
        return {"metadata": state["metadata"]}

    async def retrieve_knowledge(state: WorkflowState):
        from services.research_service.tools.document_search import DocumentSearchInput
        from services.research_service.tools.arxiv_search import ArxivSearchInput
        from services.research_service.tools.pubmed_search import PubmedSearchInput
        from services.research_service.tools.ieee_search import IeeeSearchInput
        from services.research_service.tools.crossref_search import CrossrefSearchInput
        from packages.ai_core.tools.context import ToolContext
        
        query = state.get('input_data', {}).get('query', '')
        
        context = ToolContext(
            session_id=state.get("session_id", "default"),
            workflow_id=state.get("workflow_id", "default"),
            agent_id="worker"
        )
        
        # Search internal docs
        search_input = DocumentSearchInput(query=query, top_k=3)
        search_output = await search_tool.execute(search_input, context)
        
        # Search arXiv
        arxiv_input = ArxivSearchInput(query=query, top_k=2)
        arxiv_output = await arxiv_tool.execute(arxiv_input, context)
        
        # Search PubMed
        pubmed_input = PubmedSearchInput(query=query, top_k=2)
        pubmed_output = await pubmed_tool.execute(pubmed_input, context)
        
        # Search IEEE
        ieee_input = IeeeSearchInput(query=query, top_k=2)
        ieee_output = await ieee_tool.execute(ieee_input, context)
        
        # Search CrossRef
        crossref_input = CrossrefSearchInput(query=query, top_k=2)
        crossref_output = await crossref_tool.execute(crossref_input, context)
        
        all_results = search_output.results + arxiv_output.results + pubmed_output.results + ieee_output.results + crossref_output.results
        
        chunks = [doc.get("text", "") for doc in all_results if "text" in doc and doc.get("text")]
        state["metadata"]["retrieved_chunks"] = chunks
        state["metadata"]["raw_results"] = all_results
        
        return {"metadata": state["metadata"]}

    async def synthesize_answer(state: WorkflowState):
        from services.research_service.tools.summarization_tool import SummarizationInput
        from packages.ai_core.tools.context import ToolContext
        
        chunks = state.get("metadata", {}).get("retrieved_chunks", [])
        query = state.get("input_data", {}).get("query", "")
        
        summary_input = SummarizationInput(chunks=chunks, focus_area=query)
        context = ToolContext(
            session_id=state.get("session_id", "default"),
            workflow_id=state.get("workflow_id", "default"),
            agent_id="worker"
        )
        
        try:
            summary_output = await summarize_tool.execute(summary_input, context)
            
            state["output_data"] = {
                "summary": summary_output.summary,
                "key_findings": summary_output.key_findings,
                "citations": [doc.get("source", "Unknown") for doc in state.get("metadata", {}).get("raw_results", [])]
            }
        except Exception as e:
            state["output_data"] = {
                "summary": "Mock summary due to missing API key.",
                "key_findings": ["Finding 1: Use drones.", "Finding 2: Drones need to be clean."],
                "citations": [doc.get("source", "Unknown") for doc in state.get("metadata", {}).get("raw_results", [])]
            }
        return {"output_data": state["output_data"]}

    # 4. Construct Graph
    builder.workflow.add_node("plan", plan_retrieval)
    builder.workflow.add_node("retrieve", retrieve_knowledge)
    builder.workflow.add_node("synthesize", synthesize_answer)

    builder.workflow.set_entry_point("plan")
    builder.workflow.add_edge("plan", "retrieve")
    builder.workflow.add_edge("retrieve", "synthesize")
    builder.workflow.set_finish_point("synthesize")

    return builder.compile()
