# 🧠 Casual MCP

**Casual MCP** is a Python framework for building, evaluating, and serving LLMs with tool-calling capabilities using [Model Context Protocol (MCP)](https://modelcontextprotocol.io).  
It includes:

- ✅ A multi-server MCP client
- ✅ Provider support for OpenAI + Ollama
- ✅ A recursive tool-calling chat loop
- ✅ System prompt templating with Jinja2
- ✅ A FastAPI server with CLI support

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

Providers allow access to LLMs, currently only an OpenAI provider is supplied. However in the model configuration you can supply an optional endpoint allowing you to use any `openai` compatible API (e.g LM Studio).

On the todo list is an Ollama provider and the ability to create your own custom providers to use.

---

## 🧩 System Prompt Templates

System prompts are defined as [Jinja2](https://jinja.palletsprojects.com) templates in the `prompt-templates/` directory.

They are used in the config file to specify a specific system prompt to use on the model.

This allows you to define custom system prompts for each model which is useful when using models that do not natively support tools. The templates are passed the tools list in the `tools` variable, so that you can supply the list of tools to the LLM in the prompt.

For example:
```
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

## 🚀 API Usage

### Start the API Server

```bash
casual-mcp serve --host 0.0.0.0 --port 8000
```

You can then POST to `/chat` to trigger tool-calling LLM responses.

The request takes a json body consisting of:
- `model`: the LLM model to use
- `user_prompt`: the user prompt string
- `messages`: list of chat messages (system, assistant, user, etc) that you can pass to the api, allowing you to keep your own chat session in the client calling the api
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