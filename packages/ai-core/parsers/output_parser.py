from langchain_core.output_parsers import JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel
import json

class GenericJSONParser:
    """
    Wraps LangChain's JsonOutputParser with custom fallback and validation logic.
    """
    def __init__(self, pydantic_model: BaseModel = None):
        if pydantic_model:
            self.parser = JsonOutputParser(pydantic_object=pydantic_model)
        else:
            self.parser = JsonOutputParser()
            
    def parse(self, text: str):
        try:
            return self.parser.parse(text)
        except Exception:
            # Fallback to standard json if LLM didn't return markdown ticks properly
            try:
                cleaned = text.replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned)
            except Exception as e:
                raise ValueError(f"Failed to parse LLM output: {e}")

    def get_format_instructions(self) -> str:
        return self.parser.get_format_instructions()
