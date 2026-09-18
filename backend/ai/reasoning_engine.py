from abc import ABC, abstractmethod
from typing import Any

from .decision import StructuredDecision


class ReasoningEngine(ABC):
    name = "reasoning-engine"
    version = "1.0"

    @abstractmethod
    async def decide(self, *, context: dict[str, Any]) -> StructuredDecision:
        raise NotImplementedError


    async def build_blueprint(self, *, context: dict[str, Any]):
        raise NotImplementedError
