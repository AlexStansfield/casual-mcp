import json
import os

from fastmcp import Client

from casual_mcp.logging import get_logger
from casual_mcp.models.messages import (
    ChatMessage,
    SystemMessage,
    ToolResultMessage,
    UserMessage,
)
from casual_mcp.models.tool_call import AssistantToolCall
from casual_mcp.providers.provider_factory import LLMProvider
from casual_mcp.utils import format_tool_call_result

logger = get_logger("mcp_tool_chat")
sessions: dict[str, list[ChatMessage]] = {}


class McpToolChat:
    def __init__(self, mcp_client: Client, provider: LLMProvider, system: str):
        self.provider = provider
        self.mcp_client = mcp_client
        self.system = system

    @staticmethod
    def get_session(session_id) -> list[ChatMessage] | None:
        global sessions
        return sessions.get(session_id)

    async def chat(
        self,
        prompt: str | None = None,
        messages: list[ChatMessage] = None,
        session_id: str | None = None
    ) -> list[ChatMessage]:
        global sessions

        # todo: check that we have a prompt or that there is a user message in messages

        # If we have a session ID then create if new and fetch it
        if session_id:
            if not sessions.get(session_id):
                logger.info(f"Starting new session {session_id}")
                sessions[session_id] = []
            else:
                logger.info(
                    f"Retrieving session {session_id} of length {len(sessions[session_id])}"
                )
            messages = sessions[session_id].copy()

        logger.info("Start Chat")
        async with self.mcp_client:
            tools = await self.mcp_client.list_tools()

        if messages is None or len(messages) == 0:
            message_history = []
            messages = [SystemMessage(content=self.system)]
        else:
            message_history = messages.copy()

        if prompt:
            messages.append(UserMessage(content=prompt))

        response: str | None = None
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
                        result = await self.execute(tool_call)
                    except Exception as e:
                        logger.error(e)
                        return messages
                    if result:
                        messages.append(result)
                        result_count = result_count + 1

                logger.info(f"Added {result_count} tool results")

        logger.debug(f"""Final Response:
{response} """)

        new_messages = [item for item in messages if item not in message_history]
        if session_id:
            sessions[session_id].extend(new_messages)

        return new_messages


    async def execute(self, tool_call: AssistantToolCall):
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)
        try:
            async with self.mcp_client:
                result = await self.mcp_client.call_tool(tool_name, tool_args)
        except Exception as e:
            if isinstance(e, ValueError):
                logger.warning(e)
            else:
                logger.error(f"Error calling tool: {e}")

            return ToolResultMessage(
                name=tool_call.function.name,
                tool_call_id=tool_call.id,
                content=str(e),
            )

        logger.debug(f"Tool Call Result: {result}")

        result_format = os.getenv('TOOL_RESULT_FORMAT', 'result')
        content = format_tool_call_result(tool_call, result[0].text, style=result_format)

        return ToolResultMessage(
            name=tool_call.function.name,
            tool_call_id=tool_call.id,
            content=content,
        )
