import json
from pathlib import Path

from pydantic import ValidationError

from casual_mcp.models.model_config import ModelConfig, ModelRegistry
from casual_mcp.models.tool_call import AssistantToolCall


def load_model_config(path: str | Path) -> dict[str, ModelConfig]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model config file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)
        registry = ModelRegistry.model_validate(raw_data)
        return registry.root
    except ValidationError as ve:
        raise ValueError(f"Invalid model config:\n{ve}") from ve
    except json.JSONDecodeError as je:
        raise ValueError(f"Could not parse JSON:\n{je}") from je


def format_tool_call_result(
    tool_call: AssistantToolCall, 
    result: str, 
    style: str = "function_result", 
    include_id: bool = False
    ) -> str:
    """
    Format a tool call and result into a prompt-friendly string.

    Supported styles:
        - "result": Only the result text
        - "function_result": function → result
        - "function_args_result": function(args) → result

    Include ID to add the tool call ID above the result

    Args:
        tool_call (AssistantToolCall): Tool call
        result (str): Output of the tool
        style (str): One of the supported formatting styles
        include_id (bool): Whether to include the tool call ID

    Returns:
        str: Formatted content string
    """
    func_name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)

    if style == "result":
        result_str = result

    elif style == "function_result":
        result_str = f"{func_name} → {result}"

    elif style == "function_args_result":
        arg_string = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
        result_str = f"{func_name}({arg_string}) → {result}"

    else:
        raise ValueError(f"Unsupported style: {style}")

    if (include_id):
        return f"ID: {tool_call.id}\n{result_str}"
    
    return result_str
