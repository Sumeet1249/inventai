import os
from pydantic_settings import BaseSettings

class MemoryConfig(BaseSettings):
    """
    Configuration dedicated to the AI Memory Layer.
    """
    redis_url: str = os.getenv("MEMORY_REDIS_URL", "redis://localhost:6379/3")
    vector_db_provider: str = os.getenv("VECTOR_DB_PROVIDER", "chroma")
    
    # Compression thresholds
    max_conversation_tokens: int = int(os.getenv("MAX_CONVERSATION_TOKENS", "4000"))
    enable_auto_compression: bool = os.getenv("ENABLE_AUTO_COMPRESSION", "true").lower() == "true"
    
    # TTL for short term memory
    session_ttl_seconds: int = int(os.getenv("SESSION_TTL_SECONDS", "3600"))

    class Config:
        env_file = ".env"
        extra = "ignore"

config = MemoryConfig()
