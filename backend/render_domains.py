from __future__ import annotations

import os

import requests


class RenderDomainError(RuntimeError):
    pass


def _config() -> tuple[str, str]:
    key = os.environ.get("RENDER_API_KEY", "").strip()
    service_id = os.environ.get("RENDER_FRONTEND_SERVICE_ID", "").strip()
    if not key or not service_id:
        raise RenderDomainError("Integração de domínio do Render não configurada")
    return key, service_id


def add_custom_domain(domain: str) -> dict:
    key, service_id = _config()
    response = requests.post(
        f"https://api.render.com/v1/services/{service_id}/custom-domains",
        headers={"Authorization": f"Bearer {key}"},
        json={"name": domain},
        timeout=30,
    )
    if not response.ok:
        raise RenderDomainError(f"Render recusou o domínio: HTTP {response.status_code}")
    return response.json()


def get_custom_domain(domain_id: str) -> dict:
    key, service_id = _config()
    response = requests.get(
        f"https://api.render.com/v1/services/{service_id}/custom-domains/{domain_id}",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    if not response.ok:
        raise RenderDomainError(f"Render não encontrou o domínio: HTTP {response.status_code}")
    return response.json()


def delete_custom_domain(domain_id: str) -> None:
    key, service_id = _config()
    response = requests.delete(
        f"https://api.render.com/v1/services/{service_id}/custom-domains/{domain_id}",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    if response.status_code not in {200, 204}:
        raise RenderDomainError(f"Render não removeu o domínio: HTTP {response.status_code}")
