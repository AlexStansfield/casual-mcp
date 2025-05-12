# server.py
from datetime import datetime
from typing import Annotated
from fastmcp import FastMCP
from zoneinfo import ZoneInfo
from mcp import McpError
from pydantic import BaseModel, Field

mcp = FastMCP("Time and Date 🚀")

def get_zoneinfo(timezone_name: str) -> ZoneInfo:
    try:
        return ZoneInfo(timezone_name)
    except Exception as e:
        raise McpError(f"Invalid timezone: {str(e)}")

def get_datetime(timezone_name: str) -> datetime:
    timezone = get_zoneinfo(timezone_name)
    return datetime.now(timezone)

@mcp.tool()
def get_current_time(
    timezone_name: Annotated[str, Field(description="IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Asia/Bangkok' timezone if no timezone provided by the user.")]
) -> str:
    """Get the Current Time in 24 hour format."""

    return {
        "timezone": timezone_name,
        "time": get_datetime(timezone_name).strftime("%H:%M:%S")
    }

    return f"The current time in {timezone_name} is {get_datetime(timezone_name).strftime("%H:%M:%S")}"

@mcp.tool()
def get_current_date_and_time(
    timezone_name: Annotated[str, Field(description="IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Asia/Bangkok' timezone if no timezone provided by the user.")]
) -> str:
    """Get the Current Date and Time in 24 hour format."""

    return {
        "timezone": timezone_name,
        "datetime": get_datetime(timezone_name).isoformat()
    }

    return f"The current date and time in {timezone_name} is {get_datetime(timezone_name).strftime("%H:%M:%S")}, {get_datetime(timezone_name).strftime("%A, %d %B %Y")}"


@mcp.tool()
def get_current_date(
    timezone_name: Annotated[str, Field(description="IANA timezone name (e.g., 'America/New_York', 'Europe/London'). Use 'Asia/Bangkok' timezone if no timezone provided by the user.")]
) -> str:
    """Get current time in specified timezone"""

    return {
        "timezone": timezone_name,
        "date": get_datetime(timezone_name).strftime("%Y-%m-%d")
    }

    return {
        "timezone": timezone_name,
        "date": get_datetime(timezone_name).strftime("%A, %d %B %Y")
    }

    return get_datetime(timezone_name).strftime("%A, %d %B %Y")

    return f"The current date in {timezone_name} is {get_datetime(timezone_name).strftime("%A, %d %B %Y")}"


if __name__ == "__main__":
    mcp.run()