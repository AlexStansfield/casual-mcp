from abc import ABC, abstractmethod

import mcp

from casual_mcp.models.messages import ChatMessage


class CasualMcpProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[ChatMessage],
        tools: list[mcp.Tool]
    ) -> ChatMessage:
        pass
