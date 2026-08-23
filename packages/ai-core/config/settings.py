import os
from pydantic_settings import BaseSettings


class AICoreConfig(BaseSettings):
    openai_api_key:    str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    google_api_key:    str = os.getenv("GOOGLE_API_KEY", "")

    # Primary provider: openai  (valid key available)
    # Fallback provider: gemini (only if GOOGLE_API_KEY starts with AIza...)
    default_model:    str = os.getenv("DEFAULT_LLM_MODEL",    "gpt-4o-mini")
    default_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")

    redis_url:        str = os.getenv("REDIS_URL",            "redis://localhost:6379/0")
    max_retries:      int = int(os.getenv("MAX_RETRIES",      "3"))
    timeout_seconds:  int = int(os.getenv("TIMEOUT_SECONDS",  "60"))

    class Config:
        env_file = ".env"
        extra    = "ignore"


config = AICoreConfig()
