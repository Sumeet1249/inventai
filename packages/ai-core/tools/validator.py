from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.exceptions import ToolValidationError
from pydantic import ValidationError

class ToolValidator:
    """
    Strictly validates raw dictionary inputs against the tool's Pydantic schema.
    """
    @staticmethod
    def validate_inputs(tool: BaseTool, raw_inputs: dict):
        try:
            return tool.input_schema(**raw_inputs)
        except ValidationError as e:
            raise ToolValidationError(f"Invalid inputs for tool {tool.name}: {e}")

    @staticmethod
    def validate_outputs(tool: BaseTool, raw_outputs: dict):
        try:
            return tool.output_schema(**raw_outputs)
        except ValidationError as e:
            raise ToolValidationError(f"Invalid outputs from tool {tool.name}: {e}")
