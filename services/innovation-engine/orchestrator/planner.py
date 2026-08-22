import json
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from services.innovation_engine.orchestrator.state import InnovationWorkflowState

class PlannerAgent:
    def __init__(self, llm=None):
        # Default to Gemini 2.0 Flash
        self.llm = llm or ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
        
    async def execute(self, state: InnovationWorkflowState) -> dict:
        """
        Analyzes the idea and generates an execution plan.
        """
        idea = state.get("idea", "")
        
        prompt = f"""
        You are the Master Innovation Planner.
        Analyze the following invention idea: "{idea}"
        
        Determine the required execution plan. 
        Available nodes: ["Patent", "Research", "KnowledgeGraph", "CAD", "Physics", "Report"]
        Always include Patent and Report. Include others if relevant (e.g., if it's physical, include CAD and Physics. If it requires literature review, include Research and KnowledgeGraph).
        
        Output JSON exactly in this format:
        {{"plan": ["Patent", "Research", ...]}}
        """
        
        # Simple LLM call
        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            # Basic JSON parsing
            content = response.content.strip()
            if content.startswith("```json"):
                content = content[7:-3]
            data = json.loads(content)
            plan = data.get("plan", ["Patent", "Report"])
        except Exception as e:
            # Fallback plan on error
            plan = ["Patent", "Research", "KnowledgeGraph", "CAD", "Physics", "Report"]
            
        return {
            "plan": plan,
            "logs": [f"Planner generated plan with {len(plan)} steps."],
            "current_step": "Planner"
        }
