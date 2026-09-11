"""Emergent-managed Object Storage client.

Single storage_key per process. Files are stored under a per-app prefix and a
per-company folder so tenants can't overwrite each other's files.
"""
from __future__ import annotations

import logging
import os
import uuid

import requests

logger = logging.getLogger(__name__)

_STORAGE_BASE = (os.environ.get("INTEGRATION_PROXY_URL") or "").strip() or (
    "https://integrations.emergentagent.com"
)
STORAGE_URL = _STORAGE_BASE.rstrip("/") + "/objstore/api/v1/storage"
_APP_NAME = os.environ.get("APP_NAME", "gestao-saas")

_storage_key: str | None = None


def init_storage(force: bool = False) -> str | None:
    """Provision (or refresh) the session storage_key. Never raises."""
    global _storage_key
    if _storage_key and not force:
        return _storage_key
    key = os.environ.get("EMERGENT_LLM_KEY")
    if not key:
        logger.warning("EMERGENT_LLM_KEY missing – uploads will be disabled")
        return None
    try:
        resp = requests.post(
            f"{STORAGE_URL}/init", json={"emergent_key": key}, timeout=30
        )
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        logger.info("Object storage initialized")
        return _storage_key
    except Exception as e:  # noqa: BLE001
        logger.error("Object storage init failed: %s", e)
        _storage_key = None
        return None


def put_object(path: str, data: bytes, content_type: str) -> dict:
    key = init_storage()
    if not key:
        raise RuntimeError("Storage indisponível no momento")
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data,
        timeout=120,
    )
    if resp.status_code == 404:
        # key expired – refresh once
        key = init_storage(force=True)
        if not key:
            raise RuntimeError("Storage indisponível no momento")
        resp = requests.put(
            f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key, "Content-Type": content_type},
            data=data,
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()


def get_object(path: str) -> tuple[bytes, str]:
    key = init_storage()
    if not key:
        raise RuntimeError("Storage indisponível no momento")
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key},
        timeout=60,
    )
    if resp.status_code == 404:
        key = init_storage(force=True)
        if key:
            resp = requests.get(
                f"{STORAGE_URL}/objects/{path}",
                headers={"X-Storage-Key": key},
                timeout=60,
            )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "application/octet-stream")


def build_upload_path(company_id: str, filename: str) -> str:
    ext = "bin"
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()[:8] or "bin"
    return f"{_APP_NAME}/companies/{company_id}/{uuid.uuid4().hex}.{ext}"
