from typing import Annotated, Literal
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Math Tools Server", instructions="Provides basic math operations like add, subtract, multiply, and divide.")

@mcp.tool(description="Add two numbers.")
def add(
    a: Annotated[float, Field(description="The first number")],
    b: Annotated[float, Field(description="The second number")]
) -> float:
    return a + b


@mcp.tool(description="Subtract b from a")
def subtract(
    a: Annotated[float, Field(description="The number to subtract from")],
    b: Annotated[float, Field(description="The number to subtract")]
) -> float:
    return a - b


@mcp.tool(description="Multiply two numbers.")
def multiply(
    a: Annotated[float, Field(description="The first factor")],
    b: Annotated[float, Field(description="The second factor")]
) -> float:
    return a * b


@mcp.tool(description="Divide a by b.")
def divide(
    a: Annotated[float, Field(description="The numerator")],
    b: Annotated[float, Field(description="The denominator (must not be 0)")]
) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


@mcp.tool(description="Calculate the percentage difference between two values.")
def percentage_diff(
    original: Annotated[float, Field(description="Original value")],
    new: Annotated[float, Field(description="New value")]
) -> dict:
    if original == 0:
        raise ValueError("Original value cannot be zero.")
    percent = ((new - original) / abs(original)) * 100
    return {
        "percentage_change": round(percent, 2),
        "direction": "increase" if percent > 0 else "decrease" if percent < 0 else "no change"
    }


@mcp.tool(description="Round a number to a given number of decimal places.")
def round_number(
    value: Annotated[float, Field(description="Value to round")],
    places: Annotated[int, Field(description="Number of decimal places")] = 0
) -> dict:
    return {
        "rounded_value": round(value, places),
        "decimal_places": places
    }


if __name__ == "__main__":
    mcp.run()
