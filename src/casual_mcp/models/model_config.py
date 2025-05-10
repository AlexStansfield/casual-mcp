from typing import Literal

from pydantic import BaseModel, HttpUrl, RootModel


class BaseModelConfig(BaseModel):
    provider: Literal["openai", "ollama"]
    model: str
    endpoint: HttpUrl | None = None


class OpenAIModelConfig(BaseModelConfig):
    provider: Literal["openai"]


class OllamaModelConfig(BaseModelConfig):
    provider: Literal["ollama"]


ModelConfig = OpenAIModelConfig | OllamaModelConfig


class ModelRegistry(RootModel[dict[str, ModelConfig]]):
    pass