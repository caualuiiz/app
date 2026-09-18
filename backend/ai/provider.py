from abc import ABC, abstractmethod
from typing import Any

class AIProvider(ABC):
    name = 'unknown'

    @abstractmethod
    async def generate_structured_decision(self, *, system_prompt: str, context: dict[str, Any], schema_description: str) -> dict[str, Any]:
        raise NotImplementedError
