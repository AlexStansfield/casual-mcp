import json
from pathlib import Path

from pydantic import ValidationError

from casual_mcp.models.model_config import ModelConfig, ModelRegistry


def load_model_config(path: str | Path) -> dict[str, ModelConfig]:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Model config file not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            raw_data = json.load(f)
        registry = ModelRegistry.model_validate(raw_data)
        return registry.root
    except ValidationError as ve:
        raise ValueError(f"Invalid model config:\n{ve}") from ve
    except json.JSONDecodeError as je:
        raise ValueError(f"Could not parse JSON:\n{je}") from je
