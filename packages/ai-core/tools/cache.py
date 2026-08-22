import hashlib
import json
from packages.ai_core.tools.result import ToolResult

class ToolCache:
    """
    Redis-backed cache to memoize deterministic tool outputs.
    """
    def __init__(self, redis_client=None):
        self.redis = redis_client
        self._in_memory = {}

    def _hash_inputs(self, tool_name: str, inputs: dict) -> str:
        data = json.dumps(inputs, sort_keys=True)
        return hashlib.sha256(f"{tool_name}:{data}".encode()).hexdigest()

    async def get(self, tool_name: str, inputs: dict) -> ToolResult | None:
        key = self._hash_inputs(tool_name, inputs)
        result = self._in_memory.get(key)
        if result:
            result.is_cached = True
            return result
        return None

    async def set(self, tool_name: str, inputs: dict, result: ToolResult):
        key = self._hash_inputs(tool_name, inputs)
        self._in_memory[key] = result
