"""Authentication + authorization helpers.

- Password hashing with bcrypt
- JWT access/refresh tokens (HS256)
- FastAPI dependencies: get_current_user, get_current_membership, require_roles
- Multi-tenant enforcement: tenant_id ALWAYS comes from the authenticated user's
  active membership on the backend, never from the client.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

import bcrypt
import jwt
from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Cookie, Depends, Header, HTTPException, Request, status

JWT_ALGORITHM = "HS256"
ACCESS_TTL_MIN = 60 * 24  # 24h - keeps SPA session smooth
REFRESH_TTL_DAYS = 7


def _secret() -> str:
    return os.environ["JWT_SECRET"]


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TTL_MIN),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TTL_DAYS),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, _secret(), algorithms=[JWT_ALGORITHM])


def set_auth_cookies(response, access: str, refresh: str) -> None:
    response.set_cookie(
        key="access_token", value=access, httponly=True, secure=True,
        samesite="none", max_age=ACCESS_TTL_MIN * 60, path="/",
    )
    response.set_cookie(
        key="refresh_token", value=refresh, httponly=True, secure=True,
        samesite="none", max_age=REFRESH_TTL_DAYS * 24 * 3600, path="/",
    )


def clear_auth_cookies(response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


def _extract_token(request: Request, authorization: Optional[str]) -> Optional[str]:
    tok = request.cookies.get("access_token")
    if tok:
        return tok
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


async def get_current_user(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> dict:
    """Return the authenticated user document (id as str, no password_hash)."""
    from db import get_db  # local import to avoid cycles

    token = _extract_token(request, authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Não autenticado")
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Sessão expirada")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Tipo de token inválido")

    try:
        oid = ObjectId(payload["sub"])
    except (InvalidId, KeyError):
        raise HTTPException(status_code=401, detail="Token inválido")

    db = get_db()
    user = await db.users.find_one({"_id": oid})
    if not user or user.get("status") != "ACTIVE":
        raise HTTPException(status_code=401, detail="Usuário inativo ou inexistente")
    user["id"] = str(user.pop("_id"))
    user.pop("password_hash", None)
    return user


async def get_active_membership(
    user: dict = Depends(get_current_user),
    x_company_id: Optional[str] = Header(default=None, alias="X-Company-Id"),
) -> Optional[dict]:
    """Resolve the caller's active membership for the requested company.

    The header X-Company-Id is only a HINT of which company the user wants to
    operate on when multi-membership is available. The backend always verifies
    that the (user_id, company_id) membership truly exists. If no header is
    provided, we pick the user's first active membership.

    Returns None (not an exception) so endpoints that don't need a company yet
    (e.g. onboarding) can still work.
    """
    from db import get_db

    db = get_db()
    query = {"user_id": user["id"], "status": "ACTIVE"}
    if x_company_id:
        try:
            ObjectId(x_company_id)  # sanity check
        except InvalidId:
            raise HTTPException(status_code=400, detail="ID de empresa inválido")
        query["company_id"] = x_company_id

    memb = await db.memberships.find_one(query)
    if memb:
        memb["id"] = str(memb.pop("_id"))
    return memb


async def require_membership(
    membership: Optional[dict] = Depends(get_active_membership),
) -> dict:
    if not membership:
        raise HTTPException(status_code=403, detail="Nenhuma empresa associada ao usuário")
    return membership


def require_roles(*allowed: str):
    """Return a dependency that ensures the caller's membership role is in `allowed`."""

    async def _dep(membership: dict = Depends(require_membership)) -> dict:
        if membership["role"] not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permissão insuficiente para esta ação",
            )
        return membership

    return _dep


def is_valid_object_id(value: str) -> bool:
    try:
        ObjectId(value)
        return True
    except (InvalidId, TypeError):
        return False
