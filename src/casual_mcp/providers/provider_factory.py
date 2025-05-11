import logging
import os
from typing import TypeAlias
from casual_mcp.models.model_config import ModelConfig
from casual_mcp.providers.ollama_provider import OllamaProvider
from casual_mcp.providers.openai_provider import OpenAiProvider

logger = logging.getLogger("casual_mcp.providers.factory")

LLMProvider: TypeAlias = OpenAiProvider | OllamaProvider


def provider_factory(config: ModelConfig) -> LLMProvider:
    match config.provider:
        case "ollama":
            logger.info(f"Creating Ollama provider for {config.model} at {config.endpoint}")
            return OllamaProvider(config.model, endpoint=config.endpoint.__str__())
        case "openai":
            endpoint = None
            if config.endpoint:
                endpoint = config.endpoint.__str__()

            logger.info(f"Creating OpenAI provider for {config.model} at {endpoint}")
            api_key = os.getenv("OPEN_AI_API_KEY")
            return OpenAiProvider(
                config.model,
                api_key,
                endpoint=endpoint,
            )
