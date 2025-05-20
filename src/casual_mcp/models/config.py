from typing import Dict, Optional
from pydantic import BaseModel
from casual_mcp.models.mcp_server_config import McpServerConfig
from casual_mcp.models.model_config import ModelConfig

class Config(BaseModel):
    namespace_tools: Optional[bool] = False
    models: Dict[str, ModelConfig]
    servers: Dict[str, McpServerConfig]
