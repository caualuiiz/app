"""FastAPI entrypoint for the Multi-Tenant SaaS foundation (Fase 1)."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

from fastapi import APIRouter, FastAPI  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402

from db import close_db, create_indexes, get_db  # noqa: E402
from routes_auth import router as auth_router  # noqa: E402
from routes_company import router as company_router  # noqa: E402
from routes_members import router as members_router  # noqa: E402
from routes_uploads import router as uploads_router  # noqa: E402
from routes_scheduling import (  # noqa: E402
    appts_router,
    avail_router,
    clients_router,
    dashboard_router,
    services_router,
)
from routes_landing import router as landing_router, public_router as landing_public  # noqa: E402
from routes_assistant import router as assistant_router  # noqa: E402
from routes_design import router as design_router  # noqa: E402
from storage import init_storage  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gestão SaaS – Fundação Multi-Tenant", version="1.0.0")

api_router = APIRouter(prefix="/api")


@api_router.get("/")
async def root():
    return {"message": "Gestão SaaS API", "phase": 1}


@api_router.get("/health")
async def health():
    db = get_db()
    try:
        await db.command("ping")
        return {"status": "ok"}
    except Exception:  # noqa: BLE001
        logger.exception("Health check database ping failed")
        return {"status": "degraded"}


api_router.include_router(auth_router)
api_router.include_router(company_router)
api_router.include_router(members_router)
api_router.include_router(uploads_router)
api_router.include_router(clients_router)
api_router.include_router(services_router)
api_router.include_router(avail_router)
api_router.include_router(appts_router)
api_router.include_router(dashboard_router)
api_router.include_router(landing_router)
api_router.include_router(landing_public)
api_router.include_router(assistant_router)
api_router.include_router(design_router)
app.include_router(api_router)

frontend_url = os.environ.get("FRONTEND_URL", "").strip()
allowed_origins = [o for o in [frontend_url, "http://localhost:3000"] if o]
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=allowed_origins or ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup():
    await create_indexes()
    init_storage()

    from auth import hash_password, verify_password

    db = get_db()
    admin_email = os.environ.get("ADMIN_EMAIL", "").lower().strip()
    admin_password = os.environ.get("ADMIN_PASSWORD", "")
    if admin_email and admin_password:
        existing = await db.users.find_one({"email": admin_email})
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        if existing is None:
            await db.users.insert_one({
                "name": "Administrador",
                "email": admin_email,
                "password_hash": hash_password(admin_password),
                "status": "ACTIVE",
                "created_at": now,
                "updated_at": now,
            })
            logger.info("Seeded admin user %s", admin_email)
        elif not verify_password(admin_password, existing["password_hash"]):
            await db.users.update_one(
                {"email": admin_email},
                {"$set": {
                    "password_hash": hash_password(admin_password),
                    "updated_at": now,
                }},
            )
            logger.info("Updated admin password for %s", admin_email)


@app.on_event("shutdown")
async def _shutdown():
    close_db()
