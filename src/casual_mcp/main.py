import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from casual_mcp import McpToolChat, MultiServerMCPClient
from casual_mcp.providers.provider_factory import provider_factory
from casual_mcp.utils import load_model_config, render_system_prompt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

default_system_prompt = """You are a helpful assistant.

You have access to up-to-date information through the tools, but you must never mention that tools were used.

Respond naturally and confidently, as if you already know all the facts.

**Never mention your knowledge cutoff, training data, or when you were last updated.**

You must not speculate or guess about dates — if a date is given to you by a tool, assume it is correct and respond accordingly without disclaimers.

Always present information as current and factual."""

class GenerateRequest(BaseModel):
    model: str = Field(
        title="Model to user"
    )
    system_prompt: str | None = Field(
        default=None, title="System Prompt to use"
    )
    user_prompt: str = Field(
        title="User Prompt"
    )

sys.path.append(str(Path(__file__).parent.resolve()))

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("casual_mcp.main")


async def perform_chat(model, user, system: str | None = None):
    # Get Provider from Model Config
    model_configs = load_model_config("models_config.json")
    model_config = model_configs[model]
    provider = provider_factory(model_config)

    # Create MCP Tools Client
    mcp_client = MultiServerMCPClient()

    # await mcp_client.connect_to_server_script(
    #     "../mcp-servers/amadeus/src/server.py",
    #     "flight-server",
    #     {
    #         "AMADEUS_API_KEY": os.getenv("AMADEUS_API_KEY"),
    #         "AMADEUS_API_SECRET": os.getenv("AMADEUS_API_SECRET")
    #     }
    # )
    await mcp_client.connect_to_server_script("mcp-servers/math/server.py", "math")
    await mcp_client.connect_to_server_script("mcp-servers/time-v2/server.py", "time")
    await mcp_client.connect_to_server_script("mcp-servers/weather/server.py", "weather")

    if not system:
        if (model_config.template):
            system = render_system_prompt(f"{model_config.template}.j2", await mcp_client.list_tools())
        else: 
            system = default_system_prompt

    chat = McpToolChat(mcp_client, provider, system)
    return await chat.chat(user)


async def main():
    model = "lm-phi-4-mini"
    user_prompt = "I had 8 apples and 3 oranges, then Jim gave me 3 apples and 3 oranges. In two days I will give them all to John. What date will I give them to John and how many will he get?"
    # user_prompt = "What day is it tomorrow?"
    # user_prompt = "I will give John 5 dollars every day from today. How many dollars will he have on Monday?"
    # user_prompt = "What date will next Monday be?"
    # ser_prompt = "What time is it in London?"
    return await perform_chat(model, user=user_prompt)


@app.post("/generate")
async def generate_response(req: GenerateRequest):
    messages = await perform_chat(req.model, system=req.system_prompt, user=req.user_prompt)

    return {
        "messages": messages,
        "response": messages[len(messages) - 1].content
    }

if __name__ == "__main__":
    asyncio.run(main())
