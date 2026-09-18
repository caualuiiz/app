from __future__ import annotations

import uuid
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import HTTPException

from db import get_db
from .landing_blueprint import LandingBlueprint, LandingBlueprintResponse
from .landing_brain import LandingBrain
from .render_specification import (
    RenderAccessibility,
    RenderInteractions,
    RenderMedia,
    RenderMotion,
    RenderResponsive,
    RenderSection,
    RenderSpecification,
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _latest(db, collection: str, company_id: str):
    return db[collection].find_one({"company_id": company_id}, sort=[("created_at", -1)])


def _section_type(section_id: str, purpose: str) -> str:
    allowed = {
        "hero", "about", "services", "professionals",
        "gallery", "differentiators", "hours", "contact",
    }
    if section_id in allowed:
        return section_id
    text = f"{section_id} {purpose}".lower()
    for keyword, section_type in (
        ("serv", "services"),
        ("profission", "professionals"),
        ("galeria", "gallery"),
        ("gallery", "gallery"),
        ("hor", "hours"),
        ("contat", "contact"),
        ("sobre", "about"),
        ("about", "about"),
        ("difer", "differentiators"),
    ):
        if keyword in text:
            return section_type
    return "about"


def _motion(value: str) -> str:
    text = value.lower()
    if "parallax" in text:
        return "parallax"
    if "scale" in text or "zoom" in text:
        return "scale"
    if "slide" in text:
        return "slide"
    if "fade" in text or "suave" in text:
        return "fade"
    return "none"


def _interaction(value: str) -> str:
    text = value.lower()
    if "gallery" in text or "galer" in text:
        return "gallery"
    if "accordion" in text or "acordion" in text:
        return "accordion"
    if "form" in text:
        return "form"
    if "scroll" in text:
        return "scroll"
    if "cta" in text or "agend" in text or "bot" in text:
        return "cta"
    if "link" in text:
        return "link"
    return "none"


def compile_render_spec(company: dict, blueprint: LandingBlueprint) -> RenderSpecification:
    sections = []
    for section in blueprint.layout_plan.sections:
        section_type = _section_type(section.id, section.purpose)
        image_refs = [
            placement.image_path
            for placement in blueprint.media_placements
            if section.id in placement.target_sections
        ][:12]
        content_reference_map = {
            "hero": ["landing.hero"],
            "about": ["landing.about"],
            "services": ["landing.services"],
            "professionals": ["landing.professionals"],
            "gallery": ["landing.gallery"],
            "differentiators": ["landing.differentiators"],
            "hours": ["company.hours"],
            "contact": ["company.contact"],
        }
        typography = (
            blueprint.design_system.typography.display
            if section_type == "hero"
            else blueprint.design_system.typography.heading
        )
        sections.append(
            RenderSection(
                id=section.id,
                section_type=section_type,
                layout_mode=section.layout,
                content_references=content_reference_map.get(
                    section_type, [f"landing.sections.{section.id}"]
                ),
                image_references=image_refs,
                typography=typography,
                spacing=blueprint.design_system.spacing.section,
                colors="primary/accent/background/text",
                motion=_motion(section.motion),
                interaction=_interaction(section.interaction),
                responsive_behavior=section.responsive_behavior,
                accessibility=blueprint.layout_plan.accessibility_strategy,
                fallback_behavior=(
                    "Preservar conteúdo textual e estrutura quando a mídia ou interação "
                    "não estiver disponível."
                ),
            )
        )

    return RenderSpecification(
        version="1.0",
        theme=blueprint.design_system.colors,
        typography=blueprint.design_system.typography,
        spacing=blueprint.design_system.spacing,
        sections=sections,
        motion=RenderMotion(
            intensity=blueprint.design_system.motion.intensity,
            reduced_motion="Desativar movimentos não essenciais quando prefers-reduced-motion estiver ativo.",
            fallback="Usar transições estáticas e preservar a hierarquia visual.",
        ),
        interactions=RenderInteractions(
            keyboard="Todos os controles interativos devem ser navegáveis por teclado.",
            touch="Áreas de toque devem permanecer utilizáveis em mobile.",
            focus="Estados de foco devem permanecer visíveis e consistentes.",
        ),
        responsive=RenderResponsive(
            mobile=blueprint.layout_plan.responsive_strategy,
            tablet=blueprint.layout_plan.responsive_strategy,
            desktop=blueprint.layout_plan.responsive_strategy,
        ),
        media=RenderMedia(
            lazy_loading=True,
            allowed_types=["image", "logo", "gallery"],
            fallback="Exibir fallback textual/visual seguro sem quebrar a composição.",
        ),
        accessibility=RenderAccessibility(
            contrast="Respeitar contraste adequado definido pelo Design System.",
            semantics="Usar estrutura semântica coerente com o tipo de seção.",
            alt_text="Gerar texto alternativo descritivo sem inventar fatos.",
            reduced_motion="Respeitar prefers-reduced-motion.",
        ),
    )


async def create_landing_blueprint(company_id: str, user_id: str) -> LandingBlueprintResponse:
    db = get_db()
    try:
        company = await db.companies.find_one({"_id": ObjectId(company_id)})
    except Exception as exc:
        raise HTTPException(400, "Empresa inválida") from exc

    landing = await db.landing_pages.find_one({"company_id": company_id})
    if not company or not landing:
        raise HTTPException(404, "Empresa ou landing não encontrada")

    visual = await _latest(db, "visual_profiles", company_id)
    reference = await _latest(db, "reference_profiles", company_id)
    direction = await _latest(db, "art_directions", company_id)
    system = await _latest(db, "design_systems", company_id)
    layout = await _latest(db, "layout_plans", company_id)

    context = {
        "company": {
            "name": company.get("name"),
            "business_type": company.get("business_type"),
            "description": company.get("description"),
            "city": company.get("city"),
        },
        "landing": {
            "hero": (landing.get("state") or {}).get("hero"),
            "about": (landing.get("state") or {}).get("about"),
            "style": (landing.get("state") or {}).get("style"),
            "sections": (landing.get("state") or {}).get("sections"),
        },
        "visual_intelligence": visual,
        "reference_intelligence": reference,
        "art_direction": direction,
        "design_system": system,
        "layout_plan": layout,
    }

    try:
        blueprint = await LandingBrain().build_blueprint(context=context)
    except RuntimeError as exc:
        raise HTTPException(503, "Landing Brain indisponível") from exc
    except ValueError as exc:
        raise HTTPException(502, "Blueprint rejeitado pela validação") from exc

    render_spec = compile_render_spec(company, blueprint)
    now = _now()
    request_id = str(uuid.uuid4())
    render_request_id = str(uuid.uuid4())

    await db.landing_blueprints.insert_one(
        {
            "request_id": request_id,
            "company_id": company_id,
            "user_id": user_id,
            "agent": "landing-brain",
            "agent_version": LandingBrain.version,
            "model": LandingBrain().model,
            "blueprint": blueprint.model_dump(by_alias=True),
            "created_at": now,
        }
    )
    await db.render_specifications.insert_one(
        {
            "request_id": render_request_id,
            "company_id": company_id,
            "user_id": user_id,
            "layout_plan_request_id": layout.get("request_id") if layout else None,
            "render_specification": render_spec.model_dump(by_alias=True),
            "provider": "landing-brain",
            "model": LandingBrain().model,
            "created_at": now,
        }
    )

    return LandingBlueprintResponse(
        request_id=request_id,
        company_id=company_id,
        agent="landing-brain",
        agent_version=LandingBrain.version,
        model=LandingBrain().model,
        blueprint=blueprint,
        render_spec_request_id=render_request_id,
        created_at=now,
    )
