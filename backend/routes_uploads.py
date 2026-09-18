"""Tenant image upload / download endpoints backed by MongoDB GridFS."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile

from auth import require_roles
from db import get_db
from storage import build_upload_path, get_object, put_object

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_MIME = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}
MAX_BYTES = 5 * 1024 * 1024  # 5MB


@router.post("/company-image")
async def upload_company_image(
    kind: str,
    file: UploadFile = File(...),
    membership=Depends(require_roles("OWNER", "MANAGER")),
):
    """kind ∈ {"logo", "establishment"} – updates the company document."""
    if kind not in ("logo", "establishment"):
        raise HTTPException(status_code=400, detail="Tipo de imagem inválido")
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Formato não suportado")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo excede 5MB")
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Arquivo vazio")

    path = build_upload_path(membership["company_id"], file.filename or f"image.{ALLOWED_MIME[file.content_type]}")

    try:
        result = await put_object(path, data, file.content_type)
    except Exception as e:  # noqa: BLE001
        logger.exception("Upload failed")
        raise HTTPException(status_code=502, detail=f"Falha no upload: {e}")

    stored_path = result["path"]
    db = get_db()
    now = datetime.now(timezone.utc).isoformat()

    await db.files.insert_one({
        "storage_path": stored_path,
        "company_id": membership["company_id"],
        "uploaded_by": membership["user_id"],
        "content_type": file.content_type,
        "original_filename": file.filename,
        "size": result.get("size", len(data)),
        "kind": kind,
        "is_deleted": False,
        "created_at": now,
    })

    from bson import ObjectId
    field = "logo_url" if kind == "logo" else "establishment_photo_url"
    file_url = f"/api/uploads/file/{stored_path}"
    await db.companies.update_one(
        {"_id": ObjectId(membership["company_id"])},
        {"$set": {field: file_url, "updated_at": now}},
    )
    return {"path": stored_path, "url": file_url}


@router.get("/file/{path:path}")
async def download_file(path: str, membership=Depends(require_roles("OWNER", "MANAGER", "PROFESSIONAL"))):
    """Auth-gated download. Users can only read files owned by their tenant."""
    db = get_db()
    record = await db.files.find_one({"storage_path": path, "is_deleted": False})
    if not record:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")
    if record["company_id"] != membership["company_id"]:
        raise HTTPException(status_code=403, detail="Acesso negado")
    try:
        data, content_type = await get_object(path)
    except Exception as e:  # noqa: BLE001
        logger.exception("Storage read failed")
        raise HTTPException(status_code=502, detail=f"Falha ao ler arquivo: {e}")
    return Response(content=data, media_type=record.get("content_type", content_type))
