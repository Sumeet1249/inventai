import os
from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

def get_llm(model_name: str = "gpt-4-turbo", temperature: float = 0.0) -> BaseChatModel:
    """
    Returns a configured LangChain ChatModel.
    Expects OPENAI_API_KEY environment variable to be set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is missing.")
        
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=api_key # type: ignore
    )
