from typing import Dict, Literal, Optional
from pydantic import BaseModel, RootModel


class BaseMcpServerConfig(BaseModel):
    type: Literal["python", "node", "http", "uvx"]
    system_prompt: Optional[str | None] = None


class PythonMcpServerConfig(BaseMcpServerConfig):
    type: Literal["python"] = "python"
    path: str
    env: Optional[Dict[str, str] | None] = None


class UvxMcpServerConfig(BaseMcpServerConfig):
    type: Literal["uvx"] = "uvx"
    package: str
    env: Optional[Dict[str, str] | None] = None


class NodeMcpServerConfig(BaseMcpServerConfig):
    type: Literal["node"] = "node"
    path: str
    env: Optional[Dict[str, str] | None] = None


class HttpMcpServerConfig(BaseMcpServerConfig):
    type: Literal["http"] = "http"
    endpoint: str


McpServerConfig = PythonMcpServerConfig | NodeMcpServerConfig | HttpMcpServerConfig | UvxMcpServerConfig
