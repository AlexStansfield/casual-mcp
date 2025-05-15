from typing import Annotated, Literal
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Math Tools Server", instructions="Provides basic math operations like add, subtract, multiply, and divide.")

@mcp.tool()
def add(
    a: Annotated[float, Field(description="The first number")],
    b: Annotated[float, Field(description="The second number")]
) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def subtract(
    a: Annotated[float, Field(description="The number to subtract from")],
    b: Annotated[float, Field(description="The number to subtract")]
) -> float:
    """Subtract b from a."""
    return a - b


@mcp.tool()
def multiply(
    a: Annotated[float, Field(description="The first factor")],
    b: Annotated[float, Field(description="The second factor")]
) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def divide(
    a: Annotated[float, Field(description="The numerator")],
    b: Annotated[float, Field(description="The denominator (must not be 0)")]
) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


if __name__ == "__main__":
    mcp.run()
