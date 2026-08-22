import json
from pydantic import BaseModel
from typing import Any, Dict
from packages.ai_core.memory.exceptions import SerializationError

class MemorySerializer:
    """
    Safely serializes and deserializes memory objects, handling complex
    LangChain Messages and Pydantic models.
    """
    @staticmethod
    def serialize(obj: Any) -> str:
        try:
            if isinstance(obj, BaseModel):
                return obj.model_dump_json()
            if isinstance(obj, dict):
                return json.dumps(obj, default=str)
            return json.dumps(obj)
        except Exception as e:
            raise SerializationError(f"Failed to serialize memory object: {e}")

    @staticmethod
    def deserialize(data: str) -> Dict[str, Any]:
        try:
            return json.loads(data)
        except Exception as e:
            raise SerializationError(f"Failed to deserialize memory data: {e}")
