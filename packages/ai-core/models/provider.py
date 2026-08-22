from enum import Enum

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    AZURE = "azure"
    OPENROUTER = "openrouter"
    GROQ = "groq"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"

class AIModelCapability(str, Enum):
    CHAT = "chat"
    EMBEDDING = "embedding"
    VISION = "vision"
    REASONING = "reasoning"
