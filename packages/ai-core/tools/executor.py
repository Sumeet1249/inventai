from tenacity import retry, stop_after_attempt, wait_exponential
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from packages.ai_core.tools.result import ToolResult
from packages.ai_core.tools.config import config
from packages.ai_core.tools.permissions import ToolPermissionManager
from packages.ai_core.tools.validator import ToolValidator
from packages.ai_core.tools.cache import ToolCache
from packages.ai_core.tools.metrics import ToolMetrics
from packages.ai_core.tools.exceptions import ToolExecutionError
import asyncio

cache = ToolCache()

class ToolExecutor:
    """
    The secure sandbox environment where tools are executed.
    Handles permissions, validation, retries, and timeouts.
    """
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(config.max_retries),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    async def execute(tool: BaseTool, raw_inputs: dict, context: ToolContext) -> ToolResult:
        """
        Executes a tool asynchronously with full observability and sandboxing.
        """
        # 1. Permission Check
        ToolPermissionManager.check_permissions(tool, context)
        
        # 2. Cache Check (if enabled)
        if config.enable_caching:
            cached_result = await cache.get(tool.name, raw_inputs)
            if cached_result:
                return cached_result
                
        # 3. Input Validation
        validated_inputs = ToolValidator.validate_inputs(tool, raw_inputs)
        
        # 4. Execution with Metrics & Timeout
        async def run_tool():
            return await tool.execute(validated_inputs, context)

        try:
            raw_output, latency = await ToolMetrics.track_execution(
                tool.name,
                asyncio.wait_for,
                run_tool(),
                timeout=config.timeout_ms / 1000
            )
        except asyncio.TimeoutError:
            raise ToolExecutionError(f"Tool {tool.name} exceeded timeout of {config.timeout_ms}ms")
        except Exception as e:
            raise ToolExecutionError(f"Tool {tool.name} failed: {e}")
            
        # 5. Output Validation
        validated_output = ToolValidator.validate_outputs(tool, raw_output.model_dump())
        
        # 6. Build Result
        result = ToolResult(
            success=True,
            data=validated_output.model_dump(),
            latency_ms=latency
        )
        
        # 7. Cache Save
        if config.enable_caching:
            await cache.set(tool.name, raw_inputs, result)
            
        return result
