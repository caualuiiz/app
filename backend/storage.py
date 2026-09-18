"""Tenant file storage backed by MongoDB GridFS.

New uploads no longer depend on the legacy Emergent object-storage service.
A small compatibility fallback can still read legacy objects when the optional
EMERGENT_LLM_KEY is present during migration.
"""
from __future__ import annotations

import asyncio
import logging
import os
import uuid

import requests
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from db import get_db

logger = logging.getLogger(__name__)

_BUCKET_NAME = os.environ.get("GRIDFS_BUCKET", "saas_files").strip() or "saas_files"
_LEGACY_STORAGE_BASE = (
    os.environ.get("INTEGRATION_PROXY_URL") or ""
).strip() or "https://integrations.emergentagent.com"
_LEGACY_STORAGE_URL = _LEGACY_STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
_APP_NAME = os.environ.get("APP_NAME", "gestao-saas")


def _bucket() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(get_db(), bucket_name=_BUCKET_NAME)


def build_upload_path(company_id: str, filename: str) -> str:
    ext = "bin"
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()[:8] or "bin"
    return f"{_APP_NAME}/companies/{company_id}/{uuid.uuid4().hex}.{ext}"


async def put_object(path: str, data: bytes, content_type: str) -> dict:
    gridfs_id = await _bucket().upload_from_stream(
        path,
        data,
        metadata={
            "contentType": content_type,
            "storagePath": path,
        },
    )
    return {
        "path": path,
        "size": len(data),
        "storage_id": str(gridfs_id),
        "backend": "mongodb_gridfs",
    }


async def _get_gridfs_object(path: str) -> tuple[bytes, str]:
    db = get_db()
    file_doc = await db[f"{_BUCKET_NAME}.files"].find_one({"filename": path})
    if not file_doc:
        raise FileNotFoundError(path)
    stream = await _bucket().open_download_stream(file_doc["_id"])
    data = await stream.read()
    metadata = file_doc.get("metadata") or {}
    content_type = metadata.get("contentType") or "application/octet-stream"
    return data, content_type


async def _get_legacy_object(path: str) -> tuple[bytes, str]:
    key = os.environ.get("EMERGENT_LLM_KEY", "").strip()
    if not key:
        raise FileNotFoundError(path)

    def fetch() -> requests.Response:
        return requests.get(
            f"{_LEGACY_STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key},
            timeout=60,
        )

    response = await asyncio.to_thread(fetch)
    if response.status_code == 404:
        raise FileNotFoundError(path)
    response.raise_for_status()
    return response.content, response.headers.get("Content-Type", "application/octet-stream")


async def get_object(path: str) -> tuple[bytes, str]:
    try:
        return await _get_gridfs_object(path)
    except FileNotFoundError:
        # Compatibility path for files created before the storage migration.
        return await _get_legacy_object(path)
