from tenacity import retry, stop_after_attempt, wait_exponential
from packages.ai_core.config.settings import config

def get_retry_decorator():
    """
    Returns a configured tenacity retry decorator based on global settings.
    Applies exponential backoff to handle rate limits and transient errors.
    """
    return retry(
        stop=stop_after_attempt(config.max_retries),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
