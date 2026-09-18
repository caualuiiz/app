from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from db import get_db
from auth import create_refresh_token, decode_token


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def issue_refresh_session(user_id: str) -> str:
    db = get_db()
    token = create_refresh_token(user_id)
    payload = decode_token(token)
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    await db.refresh_sessions.insert_one({
        "jti": payload["jti"],
        "user_id": user_id,
        "token_hash": _hash_token(token),
        "expires_at": exp,
        "created_at": _now(),
        "revoked_at": None,
    })
    return token


async def validate_refresh_session(token: str) -> dict:
    db = get_db()
    payload = decode_token(token)
    if payload.get("type") != "refresh" or not payload.get("jti"):
        raise ValueError("Refresh token inválido")
    session = await db.refresh_sessions.find_one({
        "jti": payload["jti"],
        "user_id": payload["sub"],
        "token_hash": _hash_token(token),
        "revoked_at": None,
    })
    if not session:
        raise ValueError("Sessão de refresh revogada ou inexistente")
    return payload


async def revoke_refresh_session(token: str) -> None:
    db = get_db()
    try:
        payload = decode_token(token)
    except Exception:
        return
    jti = payload.get("jti")
    if not jti:
        return
    await db.refresh_sessions.update_one(
        {"jti": jti},
        {"$set": {"revoked_at": _now()}},
    )
