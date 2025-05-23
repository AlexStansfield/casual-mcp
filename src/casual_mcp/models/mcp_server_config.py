from typing import Literal

from pydantic import BaseModel


class BaseMcpServerConfig(BaseModel):
    type: Literal["python", "node", "http", "uvx"]
    system_prompt: str | None | None = None


class PythonMcpServerConfig(BaseMcpServerConfig):
    type: Literal["python"] = "python"
    path: str
    env: dict[str, str] | None | None = None


class UvxMcpServerConfig(BaseMcpServerConfig):
    type: Literal["uvx"] = "uvx"
    package: str
    env: dict[str, str] | None | None = None


class NodeMcpServerConfig(BaseMcpServerConfig):
    type: Literal["node"] = "node"
    path: str
    env: dict[str, str] | None | None = None


class HttpMcpServerConfig(BaseMcpServerConfig):
    type: Literal["http"] = "http"
    url: str


McpServerConfig = (
    PythonMcpServerConfig
    | NodeMcpServerConfig
    | HttpMcpServerConfig
    | UvxMcpServerConfig
)
