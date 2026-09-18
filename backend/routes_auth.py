"""Authentication endpoints (register / login / logout / me / password reset)."""
from __future__ import annotations

import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, Response

from auth import (
    clear_auth_cookies,
    create_access_token,
    decode_token,
    get_current_user,
    hash_password,
    set_auth_cookies,
    verify_password,
)
from db import get_db
from refresh_sessions import issue_refresh_session, validate_refresh_session, revoke_refresh_session
from models import (
    AuthResponse,
    ForgotPasswordIn,
    LoginIn,
    RegisterIn,
    ResetPasswordIn,
    UserOut,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

MAX_ATTEMPTS = 5
LOCKOUT_MIN = 15


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _serialize_user(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "email": doc["email"],
        "status": doc.get("status", "ACTIVE"),
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at", doc["created_at"]),
    }


async def _load_active_context(user_id: str) -> tuple[dict | None, str | None, bool]:
    """Return (company_dict, role, needs_onboarding) for a user."""
    db = get_db()
    memb = await db.memberships.find_one({"user_id": user_id, "status": "ACTIVE"})
    if not memb:
        return None, None, True
    company = await db.companies.find_one({"_id": ObjectId(memb["company_id"])})
    if not company:
        return None, None, True
    company_out = {
        "id": str(company["_id"]),
        "name": company["name"],
        "slug": company["slug"],
        "business_type": company["business_type"],
        "logo_url": company.get("logo_url"),
        "establishment_photo_url": company.get("establishment_photo_url"),
        "description": company.get("description"),
        "phone": company.get("phone"),
        "email": company.get("email"),
        "address": company.get("address"),
        "city": company.get("city"),
        "state": company.get("state"),
        "zip_code": company.get("zip_code"),
        "status": company.get("status", "ACTIVE"),
        "created_at": company["created_at"],
        "updated_at": company.get("updated_at", company["created_at"]),
    }
    return company_out, memb["role"], False


@router.post("/register", response_model=AuthResponse)
async def register(payload: RegisterIn, response: Response):
    db = get_db()
    email = payload.email.lower().strip()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    now = _now_iso()
    doc = {
        "name": payload.name.strip(),
        "email": email,
        "password_hash": hash_password(payload.password),
        "status": "ACTIVE",
        "created_at": now,
        "updated_at": now,
    }
    result = await db.users.insert_one(doc)
    doc["_id"] = result.inserted_id
    user_out = _serialize_user(doc)

    access = create_access_token(user_out["id"], user_out["email"])
    refresh = await issue_refresh_session(user_out["id"])
    set_auth_cookies(response, access, refresh)

    return AuthResponse(user=UserOut(**user_out), needs_onboarding=True)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginIn, request: Request, response: Response):
    db = get_db()
    email = payload.email.lower().strip()
    identifier = f"{_client_ip(request)}:{email}"

    # brute-force check
    attempts_doc = await db.login_attempts.find_one({"identifier": identifier})
    if attempts_doc and attempts_doc.get("locked_until"):
        locked_until = datetime.fromisoformat(attempts_doc["locked_until"])
        if locked_until > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=429,
                detail="Muitas tentativas. Tente novamente em alguns minutos.",
            )

    user = await db.users.find_one({"email": email})
    if not user or not verify_password(payload.password, user["password_hash"]):
        # register failure
        new_count = (attempts_doc or {}).get("count", 0) + 1
        update = {"identifier": identifier, "count": new_count}
        if new_count >= MAX_ATTEMPTS:
            update["locked_until"] = (
                datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_MIN)
            ).isoformat()
            update["count"] = 0
        await db.login_attempts.update_one(
            {"identifier": identifier}, {"$set": update}, upsert=True
        )
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if user.get("status") != "ACTIVE":
        raise HTTPException(status_code=403, detail="Conta desativada")

    await db.login_attempts.delete_one({"identifier": identifier})
    user_out = _serialize_user(user)

    access = create_access_token(user_out["id"], user_out["email"])
    refresh = await issue_refresh_session(user_out["id"])
    set_auth_cookies(response, access, refresh)

    company, role, needs_onboarding = await _load_active_context(user_out["id"])
    return AuthResponse(
        user=UserOut(**user_out),
        active_company=company,
        active_role=role,
        needs_onboarding=needs_onboarding,
    )


@router.post("/logout")
async def logout(request: Request, response: Response, _user=Depends(get_current_user)):
    refresh = request.cookies.get("refresh_token")
    if refresh:
        await revoke_refresh_session(refresh)
    clear_auth_cookies(response)
    return {"success": True}


@router.get("/me", response_model=AuthResponse)
async def me(user: dict = Depends(get_current_user)):
    company, role, needs_onboarding = await _load_active_context(user["id"])
    return AuthResponse(
        user=UserOut(**user),
        active_company=company,
        active_role=role,
        needs_onboarding=needs_onboarding,
    )


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token ausente")
    try:
        payload = await validate_refresh_session(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token inválido")

    db = get_db()
    try:
        user_oid = ObjectId(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    user = await db.users.find_one({"_id": user_oid})
    if not user or user.get("status") != "ACTIVE":
        await revoke_refresh_session(token)
        raise HTTPException(status_code=401, detail="Usuário inválido")

    await revoke_refresh_session(token)
    access = create_access_token(str(user["_id"]), user["email"])
    new_refresh = await issue_refresh_session(str(user["_id"]))
    set_auth_cookies(response, access, new_refresh)
    return {"success": True}


@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordIn):
    """Structure ready – logs reset link to server logs (Fase 1)."""
    db = get_db()
    email = payload.email.lower().strip()
    user = await db.users.find_one({"email": email})
    # Always answer 200 to avoid user enumeration
    if user:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        await db.password_reset_tokens.insert_one({
            "token_hash": token_hash,
            "user_id": str(user["_id"]),
            "used": False,
            "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
            "created_at": _now_iso(),
        })
        frontend = os.environ.get("FRONTEND_URL", "").rstrip("/")
        logger.info("Password reset token created for account recovery")
    return {"success": True}


@router.post("/reset-password")
async def reset_password(payload: ResetPasswordIn):
    db = get_db()
    token_hash = hashlib.sha256(payload.token.encode("utf-8")).hexdigest()
    doc = await db.password_reset_tokens.find_one({"token_hash": token_hash})
    if not doc or doc.get("used"):
        raise HTTPException(status_code=400, detail="Token inválido ou já utilizado")
    if doc["expires_at"] < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Token expirado")

    await db.users.update_one(
        {"_id": ObjectId(doc["user_id"])},
        {"$set": {
            "password_hash": hash_password(payload.password),
            "updated_at": _now_iso(),
        }},
    )
    await db.password_reset_tokens.update_one(
        {"_id": doc["_id"]}, {"$set": {"used": True}}
    )
    # Invalidate all existing refresh sessions after a password change.
    await db.refresh_sessions.update_many(
        {"user_id": doc["user_id"], "revoked_at": None},
        {"$set": {"revoked_at": _now_iso()}},
    )
    return {"success": True}
