from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
import time
import uuid

class BaseMemorySchema(BaseModel):
    """
    Standard schema for all persisted memory objects.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    namespace: str  # e.g., 'workflow', 'session', 'project'
    owner_id: str   # user_id or agent_id
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: float = Field(default_factory=time.time)
    updated_at: float = Field(default_factory=time.time)
    version: int = 1

    def update_payload(self, new_payload: Dict[str, Any]):
        self.payload.update(new_payload)
        self.updated_at = time.time()
        self.version += 1
