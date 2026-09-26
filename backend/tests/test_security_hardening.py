import os

from fastapi import Response

from routes_uploads import _matches_image_signature
from auth import set_auth_cookies


def test_upload_signatures_match_declared_mime():
    assert _matches_image_signature("image/png", b"\x89PNG\r\n\x1a\nrest")
    assert _matches_image_signature("image/jpeg", b"\xff\xd8\xffrest")
    assert not _matches_image_signature("image/png", b"not-a-png")
    assert not _matches_image_signature("image/jpeg", b"\x89PNG\r\n\x1a\nrest")


def test_auth_cookies_are_insecure_only_in_development(monkeypatch):
    response = Response()
    monkeypatch.setenv("ENVIRONMENT", "development")
    set_auth_cookies(response, "access", "refresh")
    assert "Secure" not in response.headers["set-cookie"]

    production_response = Response()
    monkeypatch.setenv("ENVIRONMENT", "production")
    set_auth_cookies(production_response, "access", "refresh")
    assert "Secure" in production_response.headers["set-cookie"]
