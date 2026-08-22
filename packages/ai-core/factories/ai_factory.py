from packages.ai_core.models.model_registry import ModelRegistry
from packages.ai_core.memory.checkpointer import CheckpointManager
from packages.ai_core.prompts.prompt_manager import PromptManager
from packages.ai_core.agents.planner_agent import PlannerAgent
from packages.ai_core.workflows.langgraph_workflow import EnterpriseLangGraphWorkflow
from packages.ai_core.state import AgentState

class AIFactory:
    """
    Dependency Injection Container for the AI Core.
    Wires up all interfaces into a concrete Workflow.
    """
    @staticmethod
    def create_standard_workflow(provider: str = "openai", tools: list = None):
        if tools is None:
            tools = []
            
        # 1. Instantiate Core Dependencies
        llm = ModelRegistry.get_model(provider)
        checkpointer = CheckpointManager()
        prompt_manager = PromptManager()
        
        # 2. Instantiate Agents (DI)
        planner = PlannerAgent(llm=llm, prompt_manager=prompt_manager)
        
        # Dummy executor for the factory template
        async def mock_executor(state):
            return state
            
        # 3. Build Workflow
        workflow = EnterpriseLangGraphWorkflow(AgentState, checkpointer)
        workflow.build(planner_node=planner, executor_node=mock_executor, tools=tools)
        
        return workflow.compile()
