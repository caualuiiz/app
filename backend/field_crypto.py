from __future__ import annotations

import os

from cryptography.fernet import Fernet


def _fernet() -> Fernet:
    key = os.environ.get("FIELD_ENCRYPTION_KEY", "").strip()
    if not key:
        raise RuntimeError("FIELD_ENCRYPTION_KEY não configurada")
    return Fernet(key.encode())


def encrypt(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()
