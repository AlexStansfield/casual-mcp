from typing import Annotated, Literal
from fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("Math & Conversion Server", instructions="Useful utilities for calculations, percentages, rounding, and unit conversion.")
conversion_factors = {
    ("km", "mi"): 0.621371,
    ("mi", "km"): 1.60934,
    ("kg", "lb"): 2.20462,
    ("lb", "kg"): 0.453592,
    ("g", "oz"): 0.035274,
    ("oz", "g"): 28.3495,
    ("m", "ft"): 3.28084,
    ("ft", "m"): 0.3048,
    # ("c", "f"): lambda c: (c * 9 / 5) + 32,
    # ("f", "c"): lambda f: (f - 32) * 5 / 9
}


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


# @mcp.tool(description="Convert between supported units: km/mi, kg/lb, g/oz, m/ft, C/F")
# def unit_convert(
#     value: Annotated[float, Field(description="The input value")],
#     from_unit: Annotated[str, Field(description="The unit to convert from")],
#     to_unit: Annotated[str, Field(description="The unit to convert to")]
# ) -> dict:
#     key = (from_unit.lower(), to_unit.lower())
#     factor = conversion_factors.get(key)
#     if factor is None:
#         raise ValueError("Unsupported conversion.")
#     result = factor(value) if callable(factor) else value * factor
#     return {
#         "value": round(result, 4),
#         "unit": to_unit
#     }


# @mcp.tool(description="List available unit conversions and compatible pairs.")
# def list_unit_conversions() -> list:
#     pairs = sorted(set((f"{f} → {t}") for f, t in conversion_factors.keys()))
#     return pairs


if __name__ == "__main__":
    mcp.run()
