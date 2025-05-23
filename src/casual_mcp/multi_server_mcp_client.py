import json
import os

import mcp
from fastmcp import Client
from fastmcp.client.logging import LogMessage
from fastmcp.client.transports import (
    ClientTransport,
    NodeStdioTransport,
    PythonStdioTransport,
    StreamableHttpTransport,
    UvxStdioTransport,
)

from casual_mcp.logging import get_logger
from casual_mcp.models.mcp_server_config import McpServerConfig
from casual_mcp.models.messages import ToolResultMessage
from casual_mcp.models.tool_call import AssistantToolCall, AssistantToolCallFunction
from casual_mcp.utils import format_tool_call_result

logger = get_logger("multi_server_mcp_client")


async def my_log_handler(params: LogMessage):
    logger.log(params.level, params.data)


def get_server_transport(config: McpServerConfig) -> ClientTransport:
    match config.type:
        case 'python':
            return PythonStdioTransport(
                script_path=config.path,
                env=config.env
            )
        case 'node':
            return NodeStdioTransport(
                script_path=config.path,
                env=config.env
            )
        case 'http':
            return StreamableHttpTransport(
                url=config.url
                )
        case 'uvx':
            return UvxStdioTransport(
                tool_name=config.package,
                env_vars=config.env
            )


class MultiServerMCPClient:
    def __init__(self, namespace_tools: bool = False):
        self.servers: dict[str, Client] = {}  # Map server names to client connections
        self.tools_map = {}  # Map tool names to server names
        self.tools: list[mcp.types.Tool] = []
        self.system_prompts: list[str] = []
        self.namespace_tools = namespace_tools

    async def load_config(self, config: dict[str, McpServerConfig]):
        # Load the servers from config
        logger.info("Loading server config")
        for name, server_config in config.items():
            transport = get_server_transport(server_config)
            await self.connect_to_server(
                transport,
                name,
                system_prompt=server_config.system_prompt
            )


    async def connect_to_server_script(self, path, name, env={}):
        # Connect via stdio to a local script
        transport = PythonStdioTransport(
            script_path=path,
            env=env,
        )

        return await self.connect_to_server(transport, name)

    async def connect_to_server(self, server, name, system_prompt: str = None):
        """Connect to an MCP server and register its tools."""
        logger.debug(f"Connecting to server {name}")

        async with Client(
            server,
            log_handler=my_log_handler,
        ) as server_client:
            # Store the connection
            self.servers[name] = server_client

            # Fetch tools and map them to this server
            tools = await server_client.list_tools()

            # If we are namespacing servers then change the tool names
            for tool in tools:
                if self.namespace_tools:
                    tool.name = f"{name}-{tool.name}"
                else:
                    if self.tools_map.get(tool.name):
                        raise SystemError(
                            f"Tool name collision {name}:{tool.name} already added by {self.tools_map[tool.name]}"  # noqa: E501
                        )

                self.tools_map[tool.name] = name
            self.tools.extend(tools)

            if system_prompt:
                prompt = await server_client.get_prompt(system_prompt)
                if prompt:
                    self.system_prompts.append(prompt)

            return tools

    async def list_tools(self):
        """Fetch and aggregate tools from all connected servers."""
        return self.tools

    async def call_tool(self, function: AssistantToolCallFunction):
        """Route a tool call to the appropriate server."""
        tool_name = function.name
        tool_args = json.loads(function.arguments)

        # Find which server has this tool
        server_name = self.tools_map.get(tool_name)

        # Remove the sever name if the tools are namespaced
        if self.namespace_tools:
            tool_name = tool_name.removeprefix(f"{server_name}-")
        else:
            tool_name = tool_name

        if not self.tools_map.get(tool_name):
            raise ValueError(f"Tool not found: {tool_name}")

        logger.info(f"Calling tool {tool_name}")

        server_client = self.servers[server_name]
        async with server_client:
            return await server_client.call_tool(tool_name, tool_args)


    async def execute(self, tool_call: AssistantToolCall):
        try:
            result = await self.call_tool(tool_call.function)
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


    def get_system_prompts(self) -> list[str]:
        return self.system_prompts
