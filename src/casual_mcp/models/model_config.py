from typing import Literal

from pydantic import BaseModel, HttpUrl


class BaseModelConfig(BaseModel):
    provider: Literal["openai", "ollama"]
    model: str
    endpoint: HttpUrl | None = None
    template: str | None = None


class OpenAIModelConfig(BaseModelConfig):
    provider: Literal["openai"]


class OllamaModelConfig(BaseModelConfig):
    provider: Literal["ollama"]


ModelConfig = OpenAIModelConfig | OllamaModelConfig
