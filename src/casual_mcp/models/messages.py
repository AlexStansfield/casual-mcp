from typing import Literal, TypeAlias

from pydantic import BaseModel

from casual_mcp.models.tool_call import AssistantToolCall


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: str | None
    tool_calls: list[AssistantToolCall] | None


class SystemMessage(BaseModel):
    role: Literal["system"] = "system"
    content: str


class ToolResultMessage(BaseModel):
    role: Literal["tool"] = "tool"
    name: str
    tool_call_id: str
    content: str


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: str | None


CasualMcpMessage: TypeAlias = AssistantMessage | SystemMessage | ToolResultMessage | UserMessage
