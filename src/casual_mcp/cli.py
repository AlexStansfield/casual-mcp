import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from casual_mcp.utils import load_config

app = typer.Typer()
console = Console()

@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """
    Start the Casual MCP API server.
    """
    uvicorn.run(
        "casual_mcp.main:app",
        host=host,
        port=port,
        reload=reload,
        app_dir="src"
    )

@app.command()
def servers():
    """
    Return a table of all configured servers
    """
    config = load_config('config.json')
    table = Table("Name", "Type", "Path / Package / Url", "Env")

    for name, server in config.servers.items():
        path = ''
        match server.type:
            case 'python':
                path = server.path
            case 'node':
                path = server.path
            case 'http':
                path = server.url
            case 'uvx':
                path = server.package
        env = ''

        table.add_row(name, server.type, path, env)

    console.print(table)

@app.command()
def models():
    """
    Return a table of all configured models
    """
    config = load_config('config.json')
    table = Table("Name", "Provider", "Model", "Endpoint")

    for name, model in config.models.items():
        endpoint = ''
        if model.provider == 'openai':
            endpoint = model.endpoint or ''

        table.add_row(name, model.provider, model.model, str(endpoint))

    console.print(table)


if __name__ == "__main__":
    app()
