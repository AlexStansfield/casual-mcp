# 🧠 Casual MCP

![PyPI](https://img.shields.io/pypi/v/casual-mcp)
![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

**Casual MCP** is a Python framework for building, evaluating, and serving LLMs with tool-calling capabilities using [Model Context Protocol (MCP)](https://modelcontextprotocol.io).  
It includes:

- ✅ A multi-server MCP client
- ✅ Provider support for OpenAI (and OpenAI compatible APIs)
- ✅ A recursive tool-calling chat loop
- ✅ System prompt templating with Jinja2
- ✅ A basic API exposing a chat endpoint

## ✨ Features

- Plug-and-play multi-server tool orchestration
- Prompt templating with Jinja2
- Configurable via JSON
- CLI and API access
- Extensible architecture

## 🔧 Installation

```bash
pip install casual-mcp
```

Or for development:

```bash
git clone https://github.com/AlexStansfield/casual-mcp.git
cd casual-mcp
uv pip install -e .[dev]
```

## 🧩 Providers

Providers allow access to LLMs. Currently, only an OpenAI provider is supplied. However, in the model configuration, you can supply an optional `endpoint` allowing you to use any OpenAI-compatible API (e.g., LM Studio).

Ollama support is planned for a future version, along with support for custom pluggable providers via a standard interface.

## 🧩 System Prompt Templates

System prompts are defined as [Jinja2](https://jinja.palletsprojects.com) templates in the `prompt-templates/` directory.

They are used in the config file to specify a system prompt to use per model.

This allows you to define custom prompts for each model — useful when using models that do not natively support tools. Templates are passed the tool list in the `tools` variable.

```jinja2
# prompt-templates/example_prompt.j2
Here is a list of functions in JSON format that you can invoke:
[
{% for tool in tools %}
  {
    "name": "{{ tool.name }}",
    "description": "{{ tool.description }}",
    "parameters": {
    {% for param_name, param in tool.inputSchema.items() %}
      "{{ param_name }}": {
        "description": "{{ param.description }}",
        "type": "{{ param.type }}"{% if param.default is defined %},
        "default": "{{ param.default }}"{% endif %}
      }{% if not loop.last %},{% endif %}
    {% endfor %}
    }
  }{% if not loop.last %},{% endif %}
{% endfor %}
]
```

## ⚙️ Configuration File (`config.json`)

📄 See the [Programmatic Usage](#-programmatic-usage) section to build configs and messages with typed models.

The CLI and API can be configured using a `config.json` file that defines:

- 🔧 Available **models** and their providers
- 🧰 Available **MCP tool servers**
- 🧩 Optional tool namespacing behavior

### 🔸 Example

```json
{
  "namespaced_tools": false,
  "models": {
    "lm-qwen-3": {
      "provider": "openai",
      "endpoint": "http://localhost:1234/v1",
      "model": "qwen3-8b",
      "template": "lm-studio-native-tools"
    },
    "gpt-4.1": {
        "provider": "openai",
        "model": "gpt-4.1"
    }
  },
  "servers": {
    "time": {
      "type": "python",
      "path": "mcp-servers/time/server.py"
    },
    "weather": {
      "type": "http",
      "url": "http://localhost:5050/mcp"
    }
  }
}
```

### 🔹 `models`

Each model has:

- `provider`: `"openai"` or `"ollama"`
- `model`: the model name (e.g., `gpt-4.1`, `qwen3-8b`)
- `endpoint`: required for custom OpenAI-compatible backends (e.g., LM Studio)
- `template`: optional name used to apply model-specific tool calling formatting

### 🔹 `servers`

Each server has:

- `type`: `"python"`, `"http"`, `"node"`, or `"uvx"`
- For `python`/`node`: `path` to the script
- For `http`: `url` to the remote MCP endpoint
- For `uvx`: `package` for the package to run
- Optional: `env` for subprocess environments, `system_prompt` to override server prompt

### 🔹 `namespaced_tools`

If `true`, tools will be prefixed by server name (e.g., `weather-get_weather`).  
Useful for disambiguating tool names across servers and avoiding name collision if multiple servers have the same tool name.

## 🛠 CLI Reference

### `casual-mcp serve`
Start the API server.

**Options:**
- `--host`: Host to bind (default `0.0.0.0`)
- `--port`: Port to serve on (default `8000`)

### `casual-mcp servers`
Loads the config and outputs the list of MCP servers you have configured.

#### Example Output
```
$ casual-mcp servers
┏━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━┓
┃ Name    ┃ Type   ┃ Path / Package / Url          ┃ Env ┃
┡━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━┩
│ math    │ python │ mcp-servers/math/server.py    │     │
│ time    │ python │ mcp-servers/time-v2/server.py │     │
│ weather │ python │ mcp-servers/weather/server.py │     │
│ words   │ python │ mcp-servers/words/server.py   │     │
└─────────┴────────┴───────────────────────────────┴─────┘
```

### `casual-mcp models`
Loads the config and outputs the list of models you have configured.

#### Example Output
```
$ casual-mcp models
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Name              ┃ Provider ┃ Model                     ┃ Endpoint               ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ lm-phi-4-mini     │ openai   │ phi-4-mini-instruct       │ http://kovacs:1234/v1  │
│ lm-hermes-3       │ openai   │ hermes-3-llama-3.2-3b     │ http://kovacs:1234/v1  │
│ lm-groq           │ openai   │ llama-3-groq-8b-tool-use  │ http://kovacs:1234/v1  │
│ gpt-4o-mini       │ openai   │ gpt-4o-mini               │                        │
│ gpt-4.1-nano      │ openai   │ gpt-4.1-nano              │                        │
│ gpt-4.1-mini      │ openai   │ gpt-4.1-mini              │                        │
│ gpt-4.1           │ openai   │ gpt-4.1                   │                        │
└───────────────────┴──────────┴───────────────────────────┴────────────────────────┘
```

## 🧠 Programmatic Usage

You can import and use the core framework in your own Python code.

### ✅ Exposed Interfaces

#### `McpToolChat`
Orchestrates LLM interaction with tools using a recursive loop.

```python
from casual_mcp import McpToolChat

chat = McpToolChat(mcp_client, provider, system_prompt)
response = await chat.chat(prompt="What time is it in London?")
```

#### `MultiServerMCPClient`
Connects to multiple MCP tool servers and manages available tools.

```python
from casual_mcp import MultiServerMCPClient

mcp_client = MultiServerMCPClient()
await mcp_client.load_config(config["servers"])
tools = await mcp_client.list_tools()
```

#### `ProviderFactory`
Instantiates LLM providers based on the selected model config.

```python
from casual_mcp.providers.provider_factory import ProviderFactory

provider_factory = ProviderFactory()
provider = provider_factory.get_provider("lm-qwen-3", model_config)
```

#### `load_config`
Loads your `config.json` into a validated config object.

```python
from casual_mcp.utils import load_config

config = load_config("config.json")
```

#### Model and Server Configs

Exported models:
- PythonMcpServerConfig
- UvxMcpServerConfig
- NodeMcpServerConfig
- HttpMcpServerConfig
- OpenAIModelConfig

Use these types to build valid configs:

```python
from casual_mcp.models import OpenAIModelConfig, PythonMcpServerConfig

model = OpenAIModelConfig( model="llama3", endpoint="http://...")
server = PythonMcpServerConfig(path="time/server.py")
```

#### Chat Messages

Exported models:
- AssistantMessage
- SystemMessage
- ToolResultMessage
- UserMessage

Use these types to build message chains:

```python
from casual_mcp.models import SystemMessage, UserMessage

messages = [
  SystemMessage(content="You are a friendly tool calling assistant."),
  UserMessage(content="What is the time?")
]
```

### Example

```python
from casual_mcp import McpToolChat, MultiServerMCPClient, load_config, ProviderFactory
from casual_mcp.models import SystemMessage, UserMessage

model = "gpt-4.1-nano"
messages = [
  SystemMessage(content="""You are a tool calling assistant. 
You have access to up-to-date information through the tools. 
Respond naturally and confidently, as if you already know all the facts."""),
  UserMessage(content="Will I need to take my umbrella to London today?")
]

# Load the Config from the File
config = load_config("config.json")

# Setup the MultiServer MCP Client
mcp_client = MultiServerMCPClient()
await mcp_client.load_config(config.servers)

# Get the Provider for the Model
provider_factory.set_tools(await mcp_client.list_tools())
provider_factory = ProviderFactory()
provider = provider_factory.get_provider(model, config.models[model])

# Perform the Chat and Tool calling
chat = McpToolChat(mcp_client, provider, system_prompt)
response_messages = await chat.chat(messages=messages)
```

## 🚀 API Usage

### Start the API Server

```bash
casual-mcp serve --host 0.0.0.0 --port 8000
```

You can then POST to `/chat` to trigger tool-calling LLM responses.

The request takes a json body consisting of:
- `model`: the LLM model to use
- `user_prompt`: optional, the latest user message (required if messages isn't provided)
- `messages`: optional, list of chat messages (system, assistant, user, etc) that you can pass to the api, allowing you to keep your own chat session in the client calling the api
- `session_id`: an optional ID that stores all the messages from the session and provides them back to the LLM for context

You can either pass in a `user_prompt` or a list of `messages` depending on your use case.

Example:
```
{
    "session_id": "my-test-session",
    "model": "gpt-4o-mini",
    "user_prompt": "can you explain what the word consistent means?"
}
```

## License

This software is released under the [MIT License](LICENSE)