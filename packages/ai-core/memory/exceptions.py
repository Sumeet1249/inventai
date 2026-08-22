class MemoryError(Exception):
    """Base exception for all AI Memory Layer errors."""
    pass

class MemoryNotFoundError(MemoryError):
    """Raised when querying a memory ID that does not exist."""
    pass

class SerializationError(MemoryError):
    """Raised when memory contents cannot be converted to/from JSON."""
    pass

class ProviderConnectionError(MemoryError):
    """Raised when a specific memory provider (e.g., Redis, VectorDB) is unreachable."""
    pass
