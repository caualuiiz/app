"""Membership (user ↔ company) endpoints."""
from __future__ import annotations

import secrets
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from auth import (
    hash_password,
    is_valid_object_id,
    require_membership,
    require_roles,
)
from db import get_db
from models import MembershipCreate, MembershipOut, MembershipUpdate

router = APIRouter(prefix="/memberships", tags=["memberships"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _serialize(memb: dict, user: dict) -> dict:
    return {
        "id": str(memb["_id"]),
        "user_id": memb["user_id"],
        "company_id": memb["company_id"],
        "role": memb["role"],
        "status": memb.get("status", "ACTIVE"),
        "user_name": user["name"],
        "user_email": user["email"],
        "created_at": memb["created_at"],
        "updated_at": memb.get("updated_at", memb["created_at"]),
    }


@router.get("", response_model=list[MembershipOut])
async def list_memberships(membership=Depends(require_membership)):
    db = get_db()
    memberships = await db.memberships.find(
        {"company_id": membership["company_id"]}
    ).to_list(500)
    out = []
    for m in memberships:
        user = await db.users.find_one({"_id": ObjectId(m["user_id"])})
        if user:
            out.append(_serialize(m, user))
    return out


@router.post("", response_model=MembershipOut, status_code=201)
async def create_membership(
    payload: MembershipCreate,
    membership=Depends(require_roles("OWNER")),
):
    """Add a user to the current company. Creates the user if e-mail is new
    (with a random temporary password).
    """
    db = get_db()
    email = payload.email.lower().strip()

    user = await db.users.find_one({"email": email})
    if not user:
        if not payload.name:
            raise HTTPException(
                status_code=400,
                detail="Informe o nome do usuário para criar um novo cadastro",
            )
        tmp_password = secrets.token_urlsafe(12)
        now = _now_iso()
        result = await db.users.insert_one({
            "name": payload.name.strip(),
            "email": email,
            "password_hash": hash_password(tmp_password),
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
            "temporary_password": tmp_password,  # visible to OWNER once
        })
        user = await db.users.find_one({"_id": result.inserted_id})

    existing = await db.memberships.find_one({
        "user_id": str(user["_id"]),
        "company_id": membership["company_id"],
    })
    if existing:
        raise HTTPException(status_code=409, detail="Usuário já pertence à empresa")

    now = _now_iso()
    memb_doc = {
        "user_id": str(user["_id"]),
        "company_id": membership["company_id"],
        "role": payload.role,
        "status": "ACTIVE",
        "created_at": now,
        "updated_at": now,
    }
    res = await db.memberships.insert_one(memb_doc)
    memb_doc["_id"] = res.inserted_id
    return _serialize(memb_doc, user)


@router.patch("/{membership_id}", response_model=MembershipOut)
async def update_membership(
    membership_id: str,
    payload: MembershipUpdate,
    active=Depends(require_roles("OWNER")),
):
    db = get_db()
    if not is_valid_object_id(membership_id):
        raise HTTPException(status_code=400, detail="ID inválido")

    target = await db.memberships.find_one({"_id": ObjectId(membership_id)})
    if not target:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    if target["company_id"] != active["company_id"]:
        raise HTTPException(status_code=403, detail="Vínculo pertence a outra empresa")
    if str(target["_id"]) == active["id"]:
        raise HTTPException(status_code=400, detail="Não é possível alterar o próprio vínculo")

    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    updates["updated_at"] = _now_iso()

    result = await db.memberships.find_one_and_update(
        {"_id": ObjectId(membership_id)},
        {"$set": updates},
        return_document=True,
    )
    user = await db.users.find_one({"_id": ObjectId(result["user_id"])})
    return _serialize(result, user)


@router.delete("/{membership_id}")
async def delete_membership(
    membership_id: str,
    active=Depends(require_roles("OWNER")),
):
    db = get_db()
    if not is_valid_object_id(membership_id):
        raise HTTPException(status_code=400, detail="ID inválido")
    target = await db.memberships.find_one({"_id": ObjectId(membership_id)})
    if not target:
        raise HTTPException(status_code=404, detail="Vínculo não encontrado")
    if target["company_id"] != active["company_id"]:
        raise HTTPException(status_code=403, detail="Vínculo pertence a outra empresa")
    if str(target["_id"]) == active["id"]:
        raise HTTPException(status_code=400, detail="Não é possível remover o próprio vínculo")

    await db.memberships.delete_one({"_id": ObjectId(membership_id)})
    return {"success": True}
