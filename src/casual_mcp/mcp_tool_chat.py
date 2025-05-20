import logging
from typing import List
from casual_mcp.logging import get_logger
from casual_mcp.models.messages import CasualMcpMessage, SystemMessage, UserMessage
from casual_mcp.multi_server_mcp_client import MultiServerMCPClient
from casual_mcp.providers.provider_factory import LLMProvider

# logger = logging.getLogger("casual_mcp.mcp_tool_chat")
logger = get_logger("mcp_tool_chat")


class McpToolChat:
    def __init__(self, tool_client: MultiServerMCPClient, provider: LLMProvider, system: str):
        self.provider = provider
        self.tool_client = tool_client
        self.system = system

    async def chat(self, request, messages: List[CasualMcpMessage] = None):
        logger.info("Start Chat")
        tools = await self.tool_client.list_tools()

        if messages is None:
            messages = [SystemMessage(content=self.system)]

        messages.append(UserMessage(content=request))

        response = ""
        while True:
            logger.info("Calling the LLM")
            ai_message = await self.provider.generate(messages, tools)
            response = ai_message.content

            # Add the assistant's message
            messages.append(ai_message)

            if not ai_message.tool_calls:
                break

            if ai_message.tool_calls and len(ai_message.tool_calls) > 0:
                logger.info(f"Executing {len(ai_message.tool_calls)} tool calls")
                result_count = 0
                for tool_call in ai_message.tool_calls:
                    try:
                        result = await self.tool_client.execute(tool_call)
                    except Exception as e:
                        logger.error(e)
                        return messages
                    if result:
                        messages.append(result)
                        result_count = result_count + 1
                        # logger.debug(f"Added tool result: {result.model_dump_json(indent=2)}")

                logger.info(f"Added {result_count} tool results")

        logger.debug(f"""Final Response:
{response} """)

        return messages

