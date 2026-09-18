import copy
import asyncio
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from bson import ObjectId
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from ai.design_application import ApplyDesignRequest  # noqa: E402
from ai.design_application_service import apply_design  # noqa: E402
from ai.preview_application import CreatePreviewRequest  # noqa: E402
from ai.preview_service import create_preview, get_preview  # noqa: E402


def run(coro):
    return asyncio.run(coro)


class Result:
    def __init__(self, matched=0, modified=0):
        self.matched_count = matched
        self.modified_count = modified


class Cursor:
    def __init__(self, docs):
        self.docs = docs

    def sort(self, key, direction):
        self.docs.sort(key=lambda item: item.get(key), reverse=direction < 0)
        return self

    async def to_list(self, limit):
        return self.docs[:limit]


class Collection:
    def __init__(self, docs=None):
        self.docs = docs or []

    @staticmethod
    def matches(doc, query):
        for key, expected in query.items():
            if key == "$or":
                if not any(Collection.matches(doc, option) for option in expected):
                    return False
                continue
            actual = doc.get(key)
            if isinstance(expected, dict):
                if "$exists" in expected and ((key in doc) != expected["$exists"]):
                    return False
                if "$in" in expected and actual not in expected["$in"]:
                    return False
                if "$gt" in expected and not (actual > expected["$gt"]):
                    return False
            elif actual != expected:
                return False
        return True

    async def find_one(self, query, sort=None):
        found = [doc for doc in self.docs if self.matches(doc, query)]
        if sort and found:
            key, direction = sort[0]
            found.sort(key=lambda item: item.get(key), reverse=direction < 0)
        return copy.deepcopy(found[0]) if found else None

    def find(self, query):
        return Cursor([copy.deepcopy(doc) for doc in self.docs if self.matches(doc, query)])

    async def insert_one(self, doc):
        new_doc = copy.deepcopy(doc)
        new_doc.setdefault("_id", ObjectId())
        self.docs.append(new_doc)
        return type("InsertResult", (), {"inserted_id": new_doc["_id"]})()

    async def update_one(self, query, update):
        for doc in self.docs:
            if self.matches(doc, query):
                for key, value in update.get("$set", {}).items():
                    doc[key] = copy.deepcopy(value)
                return Result(1, 1)
        return Result(0, 0)


class Database:
    def __init__(self, company_id, spec):
        self.companies = Collection([{"_id": ObjectId(company_id), "name": "Studio", "status": "ACTIVE"}])
        self.landing_pages = Collection([{"company_id": company_id, "state": {"is_published": False}, "created_at": "now"}])
        self.render_specifications = Collection([{
            "request_id": "spec-1", "company_id": company_id, "render_specification": spec,
            "created_at": "2026-09-17T22:00:00+00:00",
        }])
        self.preview_sessions = Collection()
        self.draft_versions = Collection()
        self.landing_decisions = Collection()


def spec():
    return {
        "version": "1.0",
        "theme": {"primary": "#111111", "secondary": "#222222", "accent": "#C08457", "background": "#FFFFFF", "surface": "#F7F7F7", "text": "#101010", "muted": "#777777", "border": "#DDDDDD"},
        "typography": {"display": "Cormorant", "heading": "Inter", "body": "Inter", "label": "Inter", "button": "Inter"},
        "spacing": {"xs": "4px", "sm": "8px", "md": "16px", "lg": "24px", "xl": "40px", "2xl": "64px", "section": "96px"},
        "sections": [{"id": "hero", "section_type": "hero", "layout_mode": "cinematic_fullscreen", "content_references": ["landing.hero.title"], "image_references": [], "typography": "display", "spacing": "section", "colors": "theme.primary", "motion": "fade", "interaction": "cta", "responsive_behavior": "single column", "accessibility": "heading", "fallback_behavior": "legacy"}],
        "motion": {"intensity": "LOW", "reduced_motion": "disable", "fallback": "opacity"},
        "interactions": {"keyboard": "tab", "touch": "tap", "focus": "outline"},
        "responsive": {"mobile": "single", "tablet": "split", "desktop": "grid"},
        "media": {"lazy_loading": True, "allowed_types": ["image"], "fallback": "omit"},
        "accessibility": {"contrast": "AA", "semantics": "landmarks", "alt_text": "metadata", "reduced_motion": "respect"},
    }


def test_end_to_end_preview_apply_is_tenant_scoped_and_draft_only(monkeypatch):
    company_id = str(ObjectId())
    db = Database(company_id, spec())
    import ai.preview_service as preview_module
    import ai.design_application_service as apply_module
    monkeypatch.setattr(preview_module, "get_db", lambda: db)
    monkeypatch.setattr(apply_module, "get_db", lambda: db)

    preview = run(create_preview(company_id, "user-a", CreatePreviewRequest(expires_in_minutes=30)))
    applied = run(apply_design(company_id, "user-a", ApplyDesignRequest(preview_id=preview.preview_id, request_id="apply-1", expected_draft_version=0)))

    assert applied.new_version == 1
    assert applied.published is False
    assert db.landing_pages.docs[0]["draft_version"] == 1
    assert db.landing_pages.docs[0]["state"]["is_published"] is False
    assert len(db.draft_versions.docs) == 1
    assert len(db.landing_decisions.docs) == 1
    assert run(get_preview(company_id, preview.preview_id)).status == "APPLIED"

    with pytest.raises(HTTPException) as cross_tenant:
        run(get_preview(str(ObjectId()), preview.preview_id))
    assert cross_tenant.value.status_code == 404


def test_apply_is_idempotent_and_stale_version_is_rejected(monkeypatch):
    company_id = str(ObjectId())
    db = Database(company_id, spec())
    import ai.preview_service as preview_module
    import ai.design_application_service as apply_module
    monkeypatch.setattr(preview_module, "get_db", lambda: db)
    monkeypatch.setattr(apply_module, "get_db", lambda: db)

    preview = run(create_preview(company_id, "user-a", CreatePreviewRequest()))
    request = ApplyDesignRequest(preview_id=preview.preview_id, request_id="same-request", expected_draft_version=0)
    first = run(apply_design(company_id, "user-a", request))
    second = run(apply_design(company_id, "user-a", request))
    assert first.idempotent is False
    assert second.idempotent is True
    assert second.new_version == first.new_version
    assert len(db.draft_versions.docs) == 1

    second_preview = run(create_preview(company_id, "user-a", CreatePreviewRequest()))
    with pytest.raises(HTTPException) as stale:
        run(apply_design(company_id, "user-a", ApplyDesignRequest(preview_id=second_preview.preview_id, request_id="stale-request", expected_draft_version=0)))
    assert stale.value.status_code == 409
    assert db.landing_pages.docs[0]["draft_version"] == 1


def test_expired_preview_cannot_be_applied(monkeypatch):
    company_id = str(ObjectId())
    db = Database(company_id, spec())
    import ai.preview_service as preview_module
    import ai.design_application_service as apply_module
    monkeypatch.setattr(preview_module, "get_db", lambda: db)
    monkeypatch.setattr(apply_module, "get_db", lambda: db)

    preview = run(create_preview(company_id, "user-a", CreatePreviewRequest(expires_in_minutes=5)))
    db.preview_sessions.docs[0]["expires_at"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    with pytest.raises(HTTPException) as expired:
        run(apply_design(company_id, "user-a", ApplyDesignRequest(preview_id=preview.preview_id, request_id="expired-request")))
    assert expired.value.status_code == 409
    assert db.preview_sessions.docs[0]["status"] == "EXPIRED"
