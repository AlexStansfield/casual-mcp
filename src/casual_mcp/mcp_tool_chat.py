import json
import logging
from typing import List
from casual_mcp.models.messages import CasualMcpMessage, SystemMessage, UserMessage
from casual_mcp.multi_server_mcp_client import MultiServerMCPClient
from casual_mcp.providers.provider_factory import LLMProvider

logger = logging.getLogger("casual_mcp.mcp_tool_chat")


class McpToolChat:
    def __init__(self, tool_client: MultiServerMCPClient, provider: LLMProvider, system: str):
        self.provider = provider
        self.tool_client = tool_client
        self.system = system

    async def chat(self, request, messages: List[CasualMcpMessage] = []):
        if len(messages) == 0:
            messages.append(SystemMessage(content=self.system))

        messages.append(UserMessage(content=request))
        tools = await self.tool_client.list_tools()

        final_text = ""
        while True:
            ai_message = await self.provider.generate(messages, tools)
            print(ai_message)
            final_text = ai_message.content

            # Add the assistant's message
            messages.append(ai_message)
            logger.info(f"Added assistant message: {ai_message.model_dump_json(indent=2)}")

            if not ai_message.tool_calls:
                break

            for tool_call in ai_message.tool_calls:
                result = await self.tool_client.execute(tool_call)
                if result:
                    messages.append(result)
                    logger.info(f"Added tool result: {result.model_dump_json(indent=2)}")

        logger.info("========== Final Text ========")
        logger.info(final_text)

        return messages

