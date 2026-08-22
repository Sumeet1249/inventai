from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from packages.ai_core.config.settings import config
from langchain_core.language_models.chat_models import BaseChatModel
import os

class ModelRegistry:
    """
    Factory for instantiating LangChain Chat Models.
    Defaults to Google Gemini. Falls back to OpenAI if GOOGLE_API_KEY is missing.
    """
    @staticmethod
    def get_model(provider: str = None, model_name: str = None) -> BaseChatModel:
        provider = provider or config.default_provider
        model_name = model_name or config.default_model

        if provider == "gemini":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=config.google_api_key or os.getenv("GOOGLE_API_KEY"),
                temperature=0,
                max_retries=config.max_retries,
            )
        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=config.openai_api_key,
                max_retries=config.max_retries,
                timeout=config.timeout_seconds
            )
        elif provider == "anthropic":
            return ChatAnthropic(
                model=model_name,
                api_key=config.anthropic_api_key,
                max_retries=config.max_retries,
                timeout=config.timeout_seconds
            )
        else:
            raise ValueError(f"Unsupported model provider: {provider}")
