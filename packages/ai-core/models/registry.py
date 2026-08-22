from packages.ai_core.models.provider import AIProvider
from packages.ai_core.models.exceptions import UnsupportedProviderError
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = ChatGoogleGenerativeAI

try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    ChatAnthropic = ChatGoogleGenerativeAI

class ModelRegistry:
    """
    Resolves a string provider name into the corresponding LangChain implementation.
    """
    @staticmethod
    def get_langchain_class(provider: str):
        if provider == AIProvider.GEMINI or provider == "gemini":
            return ChatGoogleGenerativeAI
        elif provider == AIProvider.OPENAI:
            return ChatOpenAI
        elif provider == AIProvider.ANTHROPIC:
            return ChatAnthropic
        else:
            return ChatGoogleGenerativeAI
