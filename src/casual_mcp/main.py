import os
import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel, Field
from casual_mcp import McpToolChat, MultiServerMCPClient
from casual_mcp.logging import configure_logging, get_logger
from casual_mcp.providers.provider_factory import ProviderFactory
from casual_mcp.utils import load_config, render_system_prompt
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

load_dotenv()
config = load_config("config.json");
mcp_client = MultiServerMCPClient(namespace_tools=config.namespace_tools)
provider_factory = ProviderFactory()

app = FastAPI()

default_system_prompt = """You are a helpful assistant.

You have access to up-to-date information through the tools, but you must never mention that tools were used.

Respond naturally and confidently, as if you already know all the facts.

**Never mention your knowledge cutoff, training data, or when you were last updated.**

You must not speculate or guess about dates — if a date is given to you by a tool, assume it is correct and respond accordingly without disclaimers.

Always present information as current and factual.
"""

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
configure_logging(os.getenv("LOG_LEVEL", 'INFO'))
logger = get_logger("main")

async def perform_chat(model, user, system: str | None = None):
    # Get Provider from Model Config
    model_config = config.models[model]
    provider = provider_factory.get_provider(model, model_config)


    if not system:
        if (model_config.template):
            system = render_system_prompt(f"{model_config.template}.j2", await mcp_client.list_tools())
        else: 
            system = default_system_prompt

    chat = McpToolChat(mcp_client, provider, system)
    return await chat.chat(user)


@app.post("/generate")
async def generate_response(req: GenerateRequest):
    if len(mcp_client.tools) == 0:
        await mcp_client.load_config(config.servers)
        provider_factory.set_tools(await mcp_client.list_tools())

    messages = await perform_chat(req.model, system=req.system_prompt, user=req.user_prompt)

    return {
        "messages": messages,
        "response": messages[len(messages) - 1].content
    }

