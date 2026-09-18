from __future__ import annotations

import secrets
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from auth import is_valid_object_id, require_roles
from db import get_db
from models_domain import DomainCreate, DomainResponse
from render_domains import RenderDomainError, add_custom_domain, delete_custom_domain


router = APIRouter(prefix="/domains", tags=["domains"])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_domain(value: str) -> str:
    domain = value.strip().lower().rstrip(".")
    if "://" in domain or "/" in domain or " " in domain:
        raise HTTPException(400, "Informe apenas o domínio, sem protocolo ou caminho")
    return domain


def _out(doc: dict) -> DomainResponse:
    return DomainResponse(
        id=str(doc["_id"]),
        domain=doc["domain"],
        status=doc["status"],
        verification_record=doc["verification_record"],
        verification_value=doc["verification_value"],
        created_at=doc["created_at"],
        verified_at=doc.get("verified_at"),
    )


@router.get("", response_model=list[DomainResponse])
async def list_domains(m=Depends(require_roles("OWNER", "MANAGER"))):
    db = get_db()
    docs = await db.custom_domains.find(
        {"company_id": m["company_id"]}
    ).sort("created_at", -1).to_list(50)
    return [_out(doc) for doc in docs]


@router.post("", response_model=DomainResponse, status_code=201)
async def create_domain(payload: DomainCreate, m=Depends(require_roles("OWNER"))):
    db = get_db()
    domain = _normalize_domain(payload.domain)
    existing = await db.custom_domains.find_one({"domain": domain})

    if existing and existing.get("company_id") != m["company_id"]:
        raise HTTPException(409, "Domínio já está vinculado a outra empresa")

    if existing:
        return _out(existing)

    token = secrets.token_urlsafe(24)
    now = _now()
    doc = {
        "company_id": m["company_id"],
        "domain": domain,
        "status": "PENDING",
        "verification_record": "_saas-verification",
        "verification_value": f"saas-domain-verification={token}",
        "created_at": now,
    }
    result = await db.custom_domains.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _out(doc)


@router.post("/{domain_id}/verify", response_model=DomainResponse)
async def verify_domain(domain_id: str, m=Depends(require_roles("OWNER"))):
    if not is_valid_object_id(domain_id):
        raise HTTPException(400, "ID inválido")

    from dns.resolver import Resolver

    db = get_db()
    doc = await db.custom_domains.find_one(
        {"_id": ObjectId(domain_id), "company_id": m["company_id"]}
    )
    if not doc:
        raise HTTPException(404, "Domínio não encontrado")

    resolver = Resolver()
    try:
        answers = resolver.resolve(
            f"{doc['verification_record']}.{doc['domain']}",
            "TXT",
        )
        values = {
            str(item).strip('"')
            for answer in answers
            for item in answer.strings
        }
    except Exception as exc:
        raise HTTPException(400, "Registro TXT de verificação não encontrado") from exc

    if doc["verification_value"] not in values:
        raise HTTPException(400, "Registro TXT de verificação não corresponde")

    render_domain_id = doc.get("render_domain_id")
    render_status = doc.get("render_status")
    try:
        if not render_domain_id:
            render_domain = add_custom_domain(doc["domain"])
            render_domain_id = render_domain.get("id") or render_domain.get("name")
            render_status = render_domain.get("verification_status") or render_domain.get("status") or "PENDING"
    except RenderDomainError as exc:
        raise HTTPException(503, f"Domínio verificado no SaaS, mas o provisionamento no Render falhou: {exc}") from exc

    updated = {
        "status": "VERIFIED",
        "verified_at": _now(),
        "render_domain_id": render_domain_id,
        "render_status": render_status,
    }
    await db.custom_domains.update_one(
        {"_id": doc["_id"]},
        {"$set": updated},
    )
    doc.update(updated)
    return _out(doc)


@router.delete("/{domain_id}")
async def delete_domain(domain_id: str, m=Depends(require_roles("OWNER"))):
    if not is_valid_object_id(domain_id):
        raise HTTPException(400, "ID inválido")

    db = get_db()
    doc = await db.custom_domains.find_one({"_id": ObjectId(domain_id), "company_id": m["company_id"]})
    if doc and doc.get("render_domain_id"):
        try:
            delete_custom_domain(doc["render_domain_id"])
        except RenderDomainError:
            pass
    result = await db.custom_domains.delete_one({"_id": ObjectId(domain_id), "company_id": m["company_id"]})
    if result.deleted_count != 1:
        raise HTTPException(404, "Domínio não encontrado")
    return {"success": True}


async def resolve_custom_domain(host: str | None) -> dict | None:
    if not host:
        return None
    normalized = host.split(":", 1)[0].lower().rstrip(".")
    db = get_db()
    return await db.custom_domains.find_one(
        {"domain": normalized, "status": "VERIFIED"}
    )
