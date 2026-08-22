import pytest
from packages.ai_core.models.factory import AIModelFactory
from packages.ai_core.models.response import NormalizedAIResponse
from packages.ai_core.models.exceptions import ExhaustedFailoverError
from langchain_core.messages import HumanMessage

@pytest.mark.asyncio
async def test_factory_normalizes_response():
    """
    Validates that the AIModelFactory properly intercepts the LangChain response
    and maps it to our strict NormalizedAIResponse schema.
    """
    # This requires a mocked LangChain response
    factory = AIModelFactory(preferred_provider="openai")
    
    # Mocking the internal method to avoid hitting the real API during CI
    class MockLCResponse:
        content = "Hello from Mock OpenAI"
        response_metadata = {"token_usage": {"prompt_tokens": 10, "completion_tokens": 5}, "finish_reason": "stop"}
        
    normalized = factory._normalize_langchain_response("openai", MockLCResponse())
    
    assert isinstance(normalized, NormalizedAIResponse)
    assert normalized.provider == "openai"
    assert normalized.usage.total_tokens == 15
    assert normalized.content == "Hello from Mock OpenAI"
