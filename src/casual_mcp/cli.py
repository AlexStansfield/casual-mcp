import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """
    Start the FastAPI server.
    """
    uvicorn.run(
        "casual_mcp.main:app",
        host=host,
        port=port,
        reload=reload,
        app_dir="src"
    )


if __name__ == "__main__":
    app()