from typing import Annotated
from fastmcp import FastMCP
from pydantic import Field

# Create an MCP server
mcp = FastMCP("Demo")


# Add an addition tool
@mcp.tool()
def add(
    a: Annotated[int, Field(description="First integer")],
    b: Annotated[int, Field(description="Second integer")]
) -> int:
    """Add two integers."""
    return a + b


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run()


    