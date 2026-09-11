"""Company / tenant endpoints."""
from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from auth import get_current_user, require_membership, require_roles
from db import get_db
from models import CompanyCreate, CompanyOut, CompanyUpdate

router = APIRouter(prefix="/companies", tags=["companies"])


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "empresa"


async def _unique_slug(base: str) -> str:
    db = get_db()
    slug = base
    i = 1
    while await db.companies.find_one({"slug": slug}):
        i += 1
        slug = f"{base}-{i}"
        if i > 500:
            slug = f"{base}-{ObjectId()}"
            break
    return slug


def _serialize(doc: dict) -> dict:
    return {
        "id": str(doc["_id"]),
        "name": doc["name"],
        "slug": doc["slug"],
        "business_type": doc["business_type"],
        "logo_url": doc.get("logo_url"),
        "establishment_photo_url": doc.get("establishment_photo_url"),
        "description": doc.get("description"),
        "phone": doc.get("phone"),
        "email": doc.get("email"),
        "address": doc.get("address"),
        "city": doc.get("city"),
        "state": doc.get("state"),
        "zip_code": doc.get("zip_code"),
        "status": doc.get("status", "ACTIVE"),
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at", doc["created_at"]),
    }


@router.post("", response_model=CompanyOut, status_code=201)
async def create_company(
    payload: CompanyCreate, user: dict = Depends(get_current_user)
):
    """Create a new company AND link the caller as OWNER (onboarding)."""
    db = get_db()

    # A user without any membership uses this to onboard. Existing users can
    # still create additional companies – they'll be OWNER on the new one.
    slug = await _unique_slug(_slugify(payload.name))
    now = _now_iso()
    company_doc = {
        "name": payload.name.strip(),
        "slug": slug,
        "business_type": payload.business_type,
        "status": "ACTIVE",
        "created_at": now,
        "updated_at": now,
    }
    res = await db.companies.insert_one(company_doc)
    company_id = str(res.inserted_id)

    await db.memberships.insert_one({
        "user_id": user["id"],
        "company_id": company_id,
        "role": "OWNER",
        "status": "ACTIVE",
        "created_at": now,
        "updated_at": now,
    })

    company_doc["_id"] = res.inserted_id
    return CompanyOut(**_serialize(company_doc))


@router.get("/me", response_model=CompanyOut)
async def get_active_company(membership=Depends(require_membership)):
    db = get_db()
    company = await db.companies.find_one({"_id": ObjectId(membership["company_id"])})
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return CompanyOut(**_serialize(company))


@router.patch("/me", response_model=CompanyOut)
async def update_active_company(
    payload: CompanyUpdate,
    membership=Depends(require_roles("OWNER", "MANAGER")),
):
    db = get_db()
    updates = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
    updates["updated_at"] = _now_iso()

    # If name changes, only OWNER can rebuild slug
    if "name" in updates and membership["role"] != "OWNER":
        raise HTTPException(status_code=403, detail="Apenas o proprietário pode alterar o nome")

    if "name" in updates:
        base = _slugify(updates["name"])
        existing = await db.companies.find_one({"_id": ObjectId(membership["company_id"])})
        if existing and existing.get("slug") and _slugify(existing["name"]) == base:
            pass  # keep same slug
        else:
            updates["slug"] = await _unique_slug(base)

    result = await db.companies.find_one_and_update(
        {"_id": ObjectId(membership["company_id"])},
        {"$set": updates},
        return_document=True,
    )
    if not result:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return CompanyOut(**_serialize(result))
