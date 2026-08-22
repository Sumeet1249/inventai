from pydantic import BaseModel
from typing import Any, Optional

class ToolResult(BaseModel):
    """
    Unified result object returned by all tools.
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    is_cached: bool = False
