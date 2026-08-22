class AIModelError(Exception):
    """Base exception for all AI Model Layer errors."""
    pass

class ProviderAuthError(AIModelError):
    """Raised when an API key is invalid or missing."""
    pass

class RateLimitError(AIModelError):
    """Raised when the provider enforces a rate limit (429)."""
    pass

class ModelTimeoutError(AIModelError):
    """Raised when a request exceeds the configured timeout."""
    pass

class UnsupportedProviderError(AIModelError):
    """Raised when requesting an unknown provider."""
    pass

class ExhaustedFailoverError(AIModelError):
    """Raised when all providers in the failover chain have failed."""
    pass
