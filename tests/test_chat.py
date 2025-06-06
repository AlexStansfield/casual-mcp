import json
import pytest

from casual_mcp.mcp_tool_chat import McpToolChat
from casual_mcp.providers.abstract_provider import CasualMcpProvider
from casual_mcp.models.messages import AssistantMessage
from casual_mcp.models.tool_call import AssistantToolCall, AssistantToolCallFunction

class DummyTool:
    def __init__(self, name):
        self.name = name


class DummyResult:
    def __init__(self, text):
        self.text = text


class DummyClient:
    def __init__(self):
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def list_tools(self):
        return [DummyTool("echo")]

    async def call_tool(self, name, args):
        self.calls.append((name, args))
        return [DummyResult(text=args.get("text", ""))]

class DummyProvider(CasualMcpProvider):
    async def generate(self, messages, tools):
        return AssistantMessage(content="ok", tool_calls=None)


class ToolCallingProvider(CasualMcpProvider):
    def __init__(self):
        self.calls = 0

    async def generate(self, messages, tools):
        self.calls += 1
        if self.calls == 1:
            return AssistantMessage(
                content=None,
                tool_calls=[
                    AssistantToolCall(
                        id="1",
                        function=AssistantToolCallFunction(
                            name=tools[0].name,
                            arguments=json.dumps({"text": "hello"}),
                        ),
                    )
                ],
            )
        else:
            return AssistantMessage(content="done", tool_calls=None)

@pytest.mark.asyncio
async def test_generate_stores_session():
    chat = McpToolChat(DummyClient(), DummyProvider(), "sys")
    result = await chat.generate("hi", session_id="sess1")
    assert result[-1].content == "ok"
    session = McpToolChat.get_session("sess1")
    assert session is not None
    assert len(session) == 2


@pytest.mark.asyncio
async def test_tool_calling():
    client = DummyClient()
    provider = ToolCallingProvider()
    chat = McpToolChat(client, provider, "sys")
    messages = await chat.generate("hi")

    assert provider.calls == 2
    assert client.calls == [("echo", {"text": "hello"})]
    tool_results = [m for m in messages if getattr(m, "role", "") == "tool"]
    assert len(tool_results) == 1
    assert tool_results[0].content == "hello"
