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
    timezone_name: Annotated[str, Field(description="IANA timezone name.")]
) -> str:
    """Get the Current Time in 24 hour format. The function takes an IANA Timezone name. Use 'Asia/Bangkok' as timezone name if no timezone provided by the user."""

    return get_datetime(timezone_name).strftime("%H:%M:%S")

@mcp.tool()
def get_current_date_and_time(
    timezone_name: Annotated[str, Field(description="IANA timezone name.")]
) -> str:
    """Get the Current Date and Time in ISO 8601 format. The function takes an IANA Timezone name. Use 'Asia/Bangkok' as timezone name if no timezone provided by the user."""

    return get_datetime(timezone_name).isoformat(timespec="seconds")


@mcp.tool()
def get_current_date(
    timezone_name: Annotated[str, Field(description="IANA timezone name.")]
) -> str:
    """Get the Current Date. The function takes an IANA Timezone name. Use 'Asia/Bangkok' as timezone name if no timezone provided by the user."""

    return get_datetime(timezone_name).strftime("%A, %d %B %Y")


if __name__ == "__main__":
    mcp.run()