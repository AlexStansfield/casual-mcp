from abc import ABC, abstractmethod

import mcp

from casual_mcp.models.messages import CasualMcpMessage


class CasualMcpProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        messages: list[CasualMcpMessage],
        tools: list[mcp.Tool]
    ) -> CasualMcpMessage:
        pass
