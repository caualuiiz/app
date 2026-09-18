from typing import Any

from .decision import StructuredDecision


FORBIDDEN_KEYS = {
    "company_id", "user_id", "password", "password_hash",
    "jwt", "token", "api_key", "secret",
}


def _scan(value: Any, path: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            if normalized in FORBIDDEN_KEYS or any(
                part in normalized for part in ("api_key", "password", "secret")
            ):
                raise ValueError(f"Campo sensível não permitido: {path}.{key}")
            _scan(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan(child, f"{path}[{index}]")


def validate_decision(payload: dict[str, Any]) -> StructuredDecision:
    _scan(payload)
    return StructuredDecision.model_validate(payload)
