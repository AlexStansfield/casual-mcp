import json
import pytest

from casual_mcp.models.tool_call import AssistantToolCall, AssistantToolCallFunction
from casual_mcp.utils import format_tool_call_result

@pytest.fixture
def tool_call():
    return AssistantToolCall(
        id="abc123",
        function=AssistantToolCallFunction(name="echo", arguments=json.dumps({"text": "hi"}))
    )

def test_format_result_style_result(tool_call):
    assert format_tool_call_result(tool_call, "hello", style="result") == "hello"


def test_format_result_style_function_result(tool_call):
    assert format_tool_call_result(tool_call, "hello", style="function_result") == "echo → hello"


def test_format_result_style_function_args_result(tool_call):
    expected = "echo(text='hi') → hello"
    assert format_tool_call_result(tool_call, "hello", style="function_args_result") == expected


def test_format_result_include_id(tool_call):
    formatted = format_tool_call_result(tool_call, "hello", style="result", include_id=True)
    assert formatted.startswith("ID: abc123")
