import os

from .claude_provider import ClaudeProvider
from .provider import AIProvider


def get_ai_provider() -> AIProvider:
    provider = os.environ.get("AI_PROVIDER", "claude").strip().lower()
    if provider == "claude":
        return ClaudeProvider()
    raise RuntimeError(f"AI_PROVIDER não suportado: {provider}")
