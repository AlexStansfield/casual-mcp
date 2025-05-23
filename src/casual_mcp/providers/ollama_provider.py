from typing import Any

import mcp
import ollama
from ollama import ChatResponse, Client, ResponseError

from casual_mcp.logging import get_logger
from casual_mcp.models.generation_error import GenerationError
from casual_mcp.models.messages import AssistantMessage, CasualMcpMessage
from casual_mcp.providers.abstract_provider import CasualMcpProvider

logger = get_logger("providers.ollama")

def convert_tools(mcp_tools: list[mcp.Tool]) -> list[ollama.Tool]:
    raise Exception({"message": "under development"})


def convert_messages(messages: list[CasualMcpMessage]) -> list[ollama.Message]:
    raise Exception({"message": "under development"})


def convert_tool_calls(response_tool_calls: list[ollama.Message.ToolCall]) -> list[dict[str, Any]]:
    raise Exception({"message": "under development"})


class OllamaProvider(CasualMcpProvider):
    def __init__(self, model: str, endpoint: str = None):
        self.model = model
        self.client = Client(
            host=endpoint,
        )

    async def generate(
        self,
        messages: list[CasualMcpMessage],
        tools: list[mcp.Tool]
    ) -> CasualMcpMessage:
        logger.info("Start Generating")
        logger.debug(f"Model: {self.model}")

        # Convert tools to Ollama format
        converted_tools = convert_tools(tools)
        logger.debug(f"Converted Tools: {converted_tools}")
        logger.info(f"Adding {len(converted_tools)} tools")

        # Convert Messages to Ollama format
        converted_messages = convert_messages(messages)
        logger.debug(f"Converted Messages: {converted_messages}")

        # Call Ollama API
        try:
            response: ChatResponse = self.client.chat(
                model=self.model, messages=converted_messages, stream=False, tools=converted_tools
            )
        except ResponseError as e:
            if e.status_code == 404:
                logger.info(f"Model {self.model} not found, pulling")
                self.client.pull(self.model)
                return self.generate(messages, tools)

            raise e
        except Exception as e:
            logger.warning(f"Error in Generation: {e}")
            raise GenerationError(str(e))

        # Convert any tool calls
        tool_calls = []
        if hasattr(response.message, "tool_calls") and response.message.tool_calls:
            logger.debug(f"Assistant requested {len(response.message.tool_calls)} tool calls")
            tool_calls = convert_tool_calls(response.message.tool_calls)

        return AssistantMessage(content=response.message.content, tool_calls=tool_calls)
