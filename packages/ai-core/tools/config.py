import os
from pydantic_settings import BaseSettings

class ToolConfig(BaseSettings):
    """
    Configuration dedicated to the Tool Execution Layer.
    """
    max_retries: int = int(os.getenv("TOOL_RETRIES", "3"))
    timeout_ms: int = int(os.getenv("TOOL_TIMEOUT_MS", "15000"))
    enable_caching: bool = os.getenv("TOOL_CACHE_ENABLED", "true").lower() == "true"
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/2")
    audit_logging_enabled: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"

config = ToolConfig()
