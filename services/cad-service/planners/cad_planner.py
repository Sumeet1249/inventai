import json
import logging
from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.memory.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class CADPlanner:
    """
    Uses the AI Core to convert natural language into structured CAD parameters.
    """
    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        
    async def generate_parameters(self, idea_text: str) -> dict:
        """
        Takes a natural language idea and returns structured CAD generation parameters.
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.prompts import PromptTemplate
        from langchain_core.output_parsers import JsonOutputParser
        from pydantic import BaseModel, Field
        
        class CADParams(BaseModel):
            type: str = Field(description="The type of the object, e.g. drone, box, cylinder")
            span_mm: int = Field(description="The primary span or length dimension in mm")
            motor_count: int = Field(description="Number of motors if applicable")
            foldable: bool = Field(description="Whether the design is foldable")
            battery_compartment: bool = Field(description="Whether it needs a battery compartment")
        
        parser = JsonOutputParser(pydantic_object=CADParams)
        
        prompt = PromptTemplate(
            template="Extract CAD parameters from the following idea.\n{format_instructions}\nIdea: {idea_text}\n",
            input_variables=["idea_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
            chain = prompt | model | parser
            result = await chain.ainvoke({"idea_text": idea_text})
            
            # Ensure safe fallback values if LLM omits them
            return {
                "type": result.get("type", "drone"),
                "span_mm": result.get("span_mm", 300),
                "motor_count": result.get("motor_count", 4),
                "foldable": result.get("foldable", False),
                "battery_compartment": result.get("battery_compartment", True)
            }
        except Exception as e:
            logger.error(f"Failed to parse CAD parameters via LLM: {e}")
            # Safe default fallback
            return {
                "type": "drone",
                "span_mm": 300,
                "motor_count": 4,
                "foldable": False,
                "battery_compartment": True
            }
