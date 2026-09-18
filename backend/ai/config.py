from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AIConfig:
    provider: str
    anthropic_api_key: str
    anthropic_model: str


class ConfigurationError(RuntimeError):
    pass


def get_ai_config() -> AIConfig:
    provider = os.environ.get("AI_PROVIDER", "claude").strip().lower()
    if provider != "claude":
        raise ConfigurationError(f"AI_PROVIDER não suportado: {provider}")

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    model = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if not api_key:
        raise ConfigurationError("ANTHROPIC_API_KEY não configurada")
    if api_key.lower() in {"changeme", "replace-me", "your-key-here"}:
        raise ConfigurationError("ANTHROPIC_API_KEY ainda usa valor placeholder")
    if not model:
        raise ConfigurationError("ANTHROPIC_MODEL não configurado")
    return AIConfig(provider=provider, anthropic_api_key=api_key, anthropic_model=model)