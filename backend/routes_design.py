"""AI Digital Art Director design routes — Phase 2.1."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from auth import require_roles
from ai.art_direction import ArtDirectionListResponse, ArtDirectionResponse, GenerateArtDirectionRequest
from ai.art_direction_service import generate_art_direction, list_directions
from ai.design_system import DesignSystemListResponse, DesignSystemResponse, GenerateDesignSystemRequest
from ai.design_system_service import generate_design_system, list_design_systems
from ai.design_application import ApplyDesignRequest, ApplyDesignResponse
from ai.design_application_service import apply_design
from ai.layout_plan import GenerateLayoutPlanRequest, LayoutPlanListResponse, LayoutPlanResponse
from ai.layout_plan_service import generate_layout_plan, list_layout_plans
from ai.preview_application import CreatePreviewRequest, PreviewListResponse, PreviewResponse
from ai.preview_service import create_preview, get_preview, list_previews
from ai.render_specification import GenerateRenderSpecRequest, RenderSpecificationListResponse, RenderSpecificationResponse
from ai.render_specification_service import generate_render_spec, list_render_specs
from ai.reference import AnalyzeReferencesRequest, ReferenceProfileListResponse, ReferenceProfileResponse
from ai.reference_intelligence import analyze_references, list_profiles as list_reference_profiles
from ai.visual import AnalyzeImagesRequest, VisualProfileListResponse, VisualProfileResponse
from ai.visual_intelligence import analyze_images, list_profiles

router = APIRouter(prefix="/design", tags=["design"])


@router.post("/analyze-images", response_model=VisualProfileResponse)
async def analyze_design_images(payload: AnalyzeImagesRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await analyze_images(m["company_id"], m["user_id"], payload)


@router.get("/visual-profile", response_model=VisualProfileListResponse)
async def get_visual_profiles(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"profiles": await list_profiles(m["company_id"])}


@router.post("/analyze-references", response_model=ReferenceProfileResponse)
async def analyze_design_references(payload: AnalyzeReferencesRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await analyze_references(m["company_id"], m["user_id"], payload)


@router.get("/reference-profile", response_model=ReferenceProfileListResponse)
async def get_reference_profiles(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"profiles": await list_reference_profiles(m["company_id"])}


@router.post("/generate-art-direction", response_model=ArtDirectionResponse)
async def generate_design_art_direction(payload: GenerateArtDirectionRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await generate_art_direction(m["company_id"], m["user_id"], payload)


@router.get("/art-direction", response_model=ArtDirectionListResponse)
async def get_art_directions(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"directions": await list_directions(m["company_id"])}


@router.post("/generate-design-system", response_model=DesignSystemResponse)
async def generate_design_system_route(payload: GenerateDesignSystemRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await generate_design_system(m["company_id"], m["user_id"], payload)


@router.get("/design-system", response_model=DesignSystemListResponse)
async def get_design_systems(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"systems": await list_design_systems(m["company_id"])}


@router.post("/generate-layout-plan", response_model=LayoutPlanResponse)
async def generate_layout_plan_route(payload: GenerateLayoutPlanRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await generate_layout_plan(m["company_id"], m["user_id"], payload)


@router.get("/layout-plan", response_model=LayoutPlanListResponse)
async def get_layout_plans(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"plans": await list_layout_plans(m["company_id"])}


@router.post("/generate-render-spec", response_model=RenderSpecificationResponse)
async def generate_render_spec_route(payload: GenerateRenderSpecRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await generate_render_spec(m["company_id"], m["user_id"], payload)


@router.get("/render-spec", response_model=RenderSpecificationListResponse)
async def get_render_specs(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"specifications": await list_render_specs(m["company_id"])}


@router.post("/create-preview", response_model=PreviewResponse)
async def create_design_preview(payload: CreatePreviewRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await create_preview(m["company_id"], m["user_id"], payload)


@router.get("/preview/{preview_id}", response_model=PreviewResponse)
async def get_design_preview(preview_id: str, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await get_preview(m["company_id"], preview_id)


@router.get("/previews", response_model=PreviewListResponse)
async def get_design_previews(m=Depends(require_roles("OWNER", "MANAGER"))):
    return {"previews": await list_previews(m["company_id"])}


@router.post("/apply-preview", response_model=ApplyDesignResponse)
async def apply_design_preview(payload: ApplyDesignRequest, m=Depends(require_roles("OWNER", "MANAGER"))):
    return await apply_design(m["company_id"], m["user_id"], payload)
