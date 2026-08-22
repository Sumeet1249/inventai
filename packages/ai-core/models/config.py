import os
from pydantic_settings import BaseSettings
from typing import List, Optional

class ModelConfig(BaseSettings):
    """
    Configuration dedicated to the AI Model Layer.
    Handles multi-provider keys and global failover chains.
    """
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    azure_openai_key: Optional[str] = os.getenv("AZURE_OPENAI_KEY")
    openrouter_api_key: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Comma-separated list for failover (e.g., "openai,anthropic,gemini")
    default_failover_chain: str = os.getenv("FAILOVER_CHAIN", "openai,anthropic")
    
    max_retries: int = int(os.getenv("MODEL_RETRIES", "3"))
    timeout_ms: int = int(os.getenv("MODEL_TIMEOUT_MS", "30000"))
    
    redis_cache_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/1")
    enable_caching: bool = True

    @property
    def failover_providers(self) -> List[str]:
        return [p.strip().lower() for p in self.default_failover_chain.split(",")]

config = ModelConfig()
