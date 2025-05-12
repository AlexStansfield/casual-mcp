import logging
from typing import List
from casual_mcp.models.messages import CasualMcpMessage, SystemMessage, UserMessage
from casual_mcp.multi_server_mcp_client import MultiServerMCPClient
from casual_mcp.providers.provider_factory import LLMProvider
from casual_mcp.utils import render_system_prompt

logger = logging.getLogger("casual_mcp.mcp_tool_chat")


class McpToolChat:
    def __init__(self, tool_client: MultiServerMCPClient, provider: LLMProvider, system: str):
        self.provider = provider
        self.tool_client = tool_client
        self.system = system

    async def chat(self, request, messages: List[CasualMcpMessage] = None):
        logger.info("Start Chat")
        tools = await self.tool_client.list_tools()

        if messages is None:
            system_prompt = render_system_prompt("phi-4-mini-instruct.j2", tools)
            messages = [SystemMessage(content=system_prompt)]

        messages.append(UserMessage(content=request))

        response = ""
        while True:
            ai_message = await self.provider.generate(messages, tools)
            response = ai_message.content

            # Add the assistant's message
            messages.append(ai_message)
            logger.debug(f"Assistant Response: {ai_message.model_dump_json(indent=2)}")

            if not ai_message.tool_calls:
                break

            if ai_message.tool_calls and len(ai_message.tool_calls) > 0:
                logger.info(f"Executing {len(ai_message.tool_calls)} tool calls")
                result_count = 0
                for tool_call in ai_message.tool_calls:
                    result = await self.tool_client.execute(tool_call)
                    if result:
                        messages.append(result)
                        result_count = result_count + 1
                        logger.debug(f"Added tool result: {result.model_dump_json(indent=2)}")

                logger.info(f"Added {result_count} tool results")

        logger.debug(f"""Final Response:
{response} """)

        return messages

