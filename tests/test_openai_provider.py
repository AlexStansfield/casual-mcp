import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import importlib.util
import types
import sys
from pathlib import Path

# Stub required modules to avoid heavy dependencies
casual_mcp = types.ModuleType("casual_mcp")
sys.modules["casual_mcp"] = casual_mcp

logging_mod = types.ModuleType("casual_mcp.logging")
logging_mod.get_logger = lambda name: __import__("logging").getLogger(name)
sys.modules["casual_mcp.logging"] = logging_mod

gen_mod = types.ModuleType("casual_mcp.models.generation_error")
class GenerationError(Exception):
    pass
gen_mod.GenerationError = GenerationError
sys.modules["casual_mcp.models.generation_error"] = gen_mod

messages_mod = types.ModuleType("casual_mcp.models.messages")
class AssistantMessage:
    def __init__(self, content=None, tool_calls=None):
        self.role = "assistant"
        self.content = content
        self.tool_calls = tool_calls

class UserMessage:
    def __init__(self, content=None):
        self.role = "user"
        self.content = content

messages_mod.AssistantMessage = AssistantMessage
messages_mod.ChatMessage = object
messages_mod.UserMessage = UserMessage
sys.modules["casual_mcp.models.messages"] = messages_mod

tool_call_mod = types.ModuleType("casual_mcp.models.tool_call")
class AssistantToolCallFunction:
    def __init__(self, name: str, arguments: str, type="function"):
        self.name = name
        self.arguments = arguments
        self.type = type

class AssistantToolCall:
    def __init__(self, id, function):
        self.id = id
        self.type = "function"
        self.function = function

tool_call_mod.AssistantToolCallFunction = AssistantToolCallFunction
tool_call_mod.AssistantToolCall = AssistantToolCall
sys.modules["casual_mcp.models.tool_call"] = tool_call_mod

abstract_mod = types.ModuleType("casual_mcp.providers.abstract_provider")
class CasualMcpProvider:
    async def generate(self, messages, tools):
        pass
abstract_mod.CasualMcpProvider = CasualMcpProvider
sys.modules["casual_mcp.providers.abstract_provider"] = abstract_mod

mcp_mod = types.ModuleType("mcp")
mcp_mod.Tool = object
sys.modules["mcp"] = mcp_mod

provider_spec = importlib.util.spec_from_file_location(
    "openai_provider", Path("src/casual_mcp/providers/openai_provider.py")
)
openai_provider = importlib.util.module_from_spec(provider_spec)
provider_spec.loader.exec_module(openai_provider)
OpenAiProvider = openai_provider.OpenAiProvider


class DummyChoice:
    def __init__(self, content="hello"):
        self.message = SimpleNamespace(content=content, tool_calls=None)


def make_provider():
    return OpenAiProvider(model="test", api_key="sk-test", tools=[])


def test_generate():
    provider = make_provider()
    provider.client.chat.completions.create = AsyncMock(
        return_value=SimpleNamespace(choices=[DummyChoice("hi")])
    )

    result = asyncio.run(provider.generate([UserMessage(content="hi")], []))
    assert result.content == "hi"
    provider.client.chat.completions.create.assert_awaited()


class DummyChunk(SimpleNamespace):
    pass


def test_generate_stream():
    provider = make_provider()
    chunks = [
        DummyChunk(choices=[SimpleNamespace(delta=SimpleNamespace(content="a"))]),
        DummyChunk(choices=[SimpleNamespace(delta=SimpleNamespace(content="b"))]),
    ]

    async def async_iter():
        for c in chunks:
            yield c

    provider.client.chat.completions.create = AsyncMock(return_value=async_iter())

    result = []

    async def run():
        async for part in provider.generate_stream([UserMessage(content="hi")], []):
            result.append(part)

    asyncio.run(run())

    assert "".join(result) == "ab"
    provider.client.chat.completions.create.assert_awaited()
