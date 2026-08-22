import pytest
from packages.ai_core.memory.base_memory import BaseMemorySchema
from packages.ai_core.memory.serializer import MemorySerializer
from packages.ai_core.memory.exceptions import SerializationError
from pydantic import BaseModel

class DummyModel(BaseModel):
    name: str

def test_memory_schema_creation():
    mem = BaseMemorySchema(namespace="test", owner_id="user1", payload={"key": "value"})
    assert mem.version == 1
    
    mem.update_payload({"new_key": "new_value"})
    assert mem.version == 2
    assert mem.payload["new_key"] == "new_value"

def test_memory_serialization():
    # Dict serialization
    raw = {"data": [1, 2, 3]}
    serialized = MemorySerializer.serialize(raw)
    assert isinstance(serialized, str)
    
    deserialized = MemorySerializer.deserialize(serialized)
    assert deserialized == raw
    
    # Pydantic serialization
    pydantic_obj = DummyModel(name="test")
    serialized_model = MemorySerializer.serialize(pydantic_obj)
    assert isinstance(serialized_model, str)
