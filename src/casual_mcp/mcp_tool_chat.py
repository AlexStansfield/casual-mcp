
from casual_mcp.logging import get_logger
from casual_mcp.models.messages import CasualMcpMessage, SystemMessage, UserMessage
from casual_mcp.multi_server_mcp_client import MultiServerMCPClient
from casual_mcp.providers.provider_factory import LLMProvider

logger = get_logger("mcp_tool_chat")
sessions: dict[str, list[CasualMcpMessage]] = {}


class McpToolChat:
    def __init__(self, tool_client: MultiServerMCPClient, provider: LLMProvider, system: str):
        self.provider = provider
        self.tool_client = tool_client
        self.system = system

    @staticmethod
    def get_session(session_id) -> list[CasualMcpMessage] | None:
        global sessions
        return sessions.get(session_id)

    async def chat(
        self,
        prompt: str | None = None,
        messages: list[CasualMcpMessage] = None,
        session_id: str | None = None
    ) -> list[CasualMcpMessage]:
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
        tools = await self.tool_client.list_tools()

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
                        result = await self.tool_client.execute(tool_call)
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

