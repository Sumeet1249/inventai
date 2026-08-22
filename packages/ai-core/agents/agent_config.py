import os
from pydantic_settings import BaseSettings

class AgentConfig(BaseSettings):
    """Configuration dedicated to the Agent Framework."""
    max_agent_retries: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
    agent_timeout_seconds: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "120"))
    enable_agent_telemetry: bool = os.getenv("ENABLE_AGENT_TELEMETRY", "true").lower() == "true"
    max_delegation_depth: int = int(os.getenv("MAX_DELEGATION_DEPTH", "5"))

    class Config:
        env_file = ".env"
        extra = "ignore"

config = AgentConfig()
