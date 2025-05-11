import json
import logging

import mcp
from fastmcp import Client
from fastmcp.client.logging import LogMessage
from fastmcp.client.transports import PythonStdioTransport

from casual_mcp.models.messages import ToolResultMessage
from casual_mcp.models.tool_call import AssistantToolCall, AssistantToolCallFunction

logger = logging.getLogger("casual_mcp.multi_server_mcp_client")


async def my_log_handler(params: LogMessage):
    logger.log(params.level, params.data)


class MultiServerMCPClient:
    def __init__(self):
        self.servers: dict[str, Client] = {}  # Map server names to client connections
        self.tools_map = {}  # Map tool names to server names
        self.tools: list[mcp.types.Tool] = []

    async def connect_to_server_script(self, path, name, env={}):
        # Connect via stdio to a local script
        transport = PythonStdioTransport(
            script_path=path,
            env=env,
        )

        return await self.connect_to_server(transport, name)

    async def connect_to_server(self, server, name):
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
            self.tools.extend(tools)
            for tool in tools:
                self.tools_map[tool.name] = name

            return tools

    async def list_tools(self):
        """Fetch and aggregate tools from all connected servers."""
        return self.tools

    async def call_tool(self, function: AssistantToolCallFunction):
        """Route a tool call to the appropriate server."""
        tool_name = function.name
        tool_args = json.loads(function.arguments)

        if not self.tools_map[tool_name]:
            raise ValueError(f"Tool not found: {tool_name}")

        logger.debug(f"Calling tool {tool_name}")

        # Find which server has this tool
        server_name = self.tools_map.get(tool_name)
        server_client = self.servers[server_name]
        async with server_client:
            logger.debug(f"Tool Arguments {tool_args}")
            return await server_client.call_tool(tool_name, tool_args)
        

    async def execute(self, tool_call: AssistantToolCall):
        result = await self.call_tool(tool_call.function)

        logger.debug(f"Tool Call Result: {result}")

        return ToolResultMessage(
            name=tool_call.function.name,
            tool_call_id=tool_call.id,
            content=", ".join([ob.text for ob in result]),
        )
