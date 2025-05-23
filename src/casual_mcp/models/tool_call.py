from typing import Literal

from pydantic import BaseModel


class AssistantToolCallFunction(BaseModel):
    name: str
    arguments: str


class AssistantToolCall(BaseModel):
    id: str
    type: Literal["function"] = "function"
    function: AssistantToolCallFunction
