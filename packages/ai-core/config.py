import os
from pydantic_settings import BaseSettings

class AICoreConfig(BaseSettings):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    default_model: str = os.getenv("DEFAULT_LLM_MODEL", "gpt-4-turbo")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    max_retries: int = 3
    timeout_seconds: int = 60

    class Config:
        env_file = ".env"

config = AICoreConfig()
