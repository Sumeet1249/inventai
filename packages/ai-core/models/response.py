from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class NormalizedAIResponse(BaseModel):
    """
    The unified response object that all services will receive,
    regardless of whether the backend was OpenAI, Anthropic, or Groq.
    """
    content: str
    provider: str
    model: str
    
    usage: TokenUsage = Field(default_factory=TokenUsage)
    cost_usd: float = 0.0
    latency_ms: float = 0.0
    
    finish_reason: str = "stop" # stop, length, content_filter, tool_calls
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    is_cached: bool = False
