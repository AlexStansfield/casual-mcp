# 🧠 casual-mcp

**casual-mcp** is a Python framework for building, evaluating, and serving LLMs with tool-calling capabilities using [Model Context Protocol (MCP)](https://modelcontextprotocol.io).  
It includes:

- ✅ A multi-server MCP client
- ✅ Provider support for OpenAI + Ollama
- ✅ A recursive tool-calling chat loop
- ✅ System prompt templating with Jinja2
- ✅ A FastAPI server with CLI support

---

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

---

## 🚀 Usage

### Start the API Server

```bash
casual-mcp serve --host 0.0.0.0 --port 8000
```

You can then POST to `/chat` to trigger tool-calling LLM responses.

---

## 🧩 Prompt Templates

System prompts are defined as [Jinja2](https://jinja.palletsprojects.com) templates in the `prompt-templates/` directory.

---

## 🛠 CLI Reference

### `casual-mcp serve`
Start the FastAPI server.

**Options:**
- `--host`: Host to bind (default `0.0.0.0`)
- `--port`: Port to serve on (default `8000`)

---

## 📁 Project Structure

```
casual_mcp/
├── cli.py                 ← CLI entrypoint
├── main.py                ← FastAPI app
├── prompts/loader.py      ← System prompt renderer
├── models/                ← Pydantic model config
├── providers/             ← LLM providers (OpenAI, Ollama)
├── utils.py               ← General utilities
├── config.py              ← CLI-accessible runtime state
```

---

## 📦 Publishing Notes

This package uses `pyproject.toml` and `setup.cfg` for installation and CLI script support.

To build and upload:

```bash
uv pip install build twine
python -m build
twine upload dist/*
```

---

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
    "ollama-phi": {
      "provider": "ollama",
      "endpoint": "http://localhost:11434",
      "model": "phi4-tools"
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
Useful for disambiguating tool names across servers and avoiding collision if multiple servers have the same tool name

---

## License

MIT