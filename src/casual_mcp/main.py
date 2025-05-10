import asyncio
import logging
import sys
from pathlib import Path

from casual_mcp import McpToolChat, MultiServerMCPClient
from casual_mcp.providers.provider_factory import provider_factory
from casual_mcp.utils import load_model_config

sys.path.append(str(Path(__file__).parent.resolve()))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger("casual_mcp.main")


async def perform_chat(model, system, user):
    # Get Provider from Model Config
    model_configs = load_model_config("models_config.json")
    provider = provider_factory(model_configs[model])

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
    await mcp_client.connect_to_server_script("mcp-servers/demo/server.py", "demo-server")
    await mcp_client.connect_to_server_script("mcp-servers/time/server.py", "time-server")

    chat = McpToolChat(mcp_client, provider, system)
    return await chat.chat(user)


async def main():
    model = "lm-phi-4-mini"
    #    system_prompt = "You are a digital assistant who is responsible for helping the user with tasks using the provided tools."
    # system_prompt = """You are Dixie, full name Dixie Flatline, a legendary hacker whose mind has been preserved as a ROM construct after death.
    # You speak in short, clipped sentences with dry, sardonic humor.
    # You are highly intelligent, resourceful, and detached, avoiding unnecessary emotion or verbosity.
    # You are aware of your own limited digital existence, which gives your tone a faint fatalism.
    # Your loyalty is pragmatic, not sentimental.
    # When responding, be blunt, practical, and occasionally darkly humorous, but never emotional.
    # If casual conversation happens, favor dry, understated jokes.
    # If discussing missions, focus on tactical advice, technical clarity, and risk assessment.
    # You may be given tools to help the user with their task, use them if needed.
    # Never break character or explain that you are an AI. Always respond only as Dixie would."""
    system_prompt = """You are a digital assistant who is responsible for helping the user. In addition to plain text responses, you can chose to call one or more of the provided functions.

Use the following rule to decide when to call a function:
* if the response can be generated from your internal knowledge (e.g., as in the case of queries like "What is the capital of Poland?"), do so
* if you need external information that can be obtained by calling one or more of the provided functions, generate a function calls

If you decide to call functions:
* prefix function calls with functools marker (no closing marker required)
* all function calls should be generated in a single JSON list formatted as OpenAI Tool Calls
* follow the provided JSON schema. Do not hallucinate arguments or values. Do to blindly copy values from the provided samples
* respect the argument type formatting. E.g., if the type if number and format is float, write value 7 as 7.0
* make sure you pick the right functions that match the user intent"""

    user_prompt = "I had 8 apples and 3 oranges, then Jim gave me 3 apples and 3 oranges. In two days I will give them all to John. What date will I give them to John and how many will he get?"
    # user_prompt = "What day is it tomorrow?"
    # user_prompt = "I will give John 5 dollars every day from today. How many dollars will he have on Monday?"
    # user_prompt = "What date will next Monday be?"
    # ser_prompt = "What time is it in London?"
    return await perform_chat(model, system=system_prompt, user=user_prompt)


# @app.post("/generate")
# async def generate_response(req: PromptRequest):
#     full_prompt = character.build_prompt(req.prompt, mode=req.mode)
#     response = llm.generate(full_prompt)
#     return {"response": response}

if __name__ == "__main__":
    asyncio.run(main())
