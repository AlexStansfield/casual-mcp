from typing import Literal, Optional
from pydantic import BaseModel, RootModel


class BaseMcpServerConfig(BaseModel):
    type: Literal["python", "node", "http", "uvx"]
    system_prompt: Optional[str | None] = None


class PythonMcpServerConfig(BaseMcpServerConfig):
    type: Literal["python"]
    path: str


class UvxMcpServerConfig(BaseMcpServerConfig):
    type: Literal["uvx"]
    package: str


class NodeMcpServerConfig(BaseMcpServerConfig):
    type: Literal["node"]
    path: str


class HttpMcpServerConfig(BaseMcpServerConfig):
    type: Literal["http"]
    endpoint: str


McpServerConfig = PythonMcpServerConfig | NodeMcpServerConfig | HttpMcpServerConfig | UvxMcpServerConfig


class McpServerConfigRegistry(RootModel[dict[str, McpServerConfig]]):
    pass