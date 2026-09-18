"""AI Digital Art Director design routes — Phase 2.1."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from auth import require_roles
from ai.art_direction import ArtDirectionListResponse, ArtDirectionResponse, GenerateArtDirectionRequest
from ai.art_direction_service import generate_art_direction, list_directions
from ai.design_system import DesignSystemListResponse, DesignSystemResponse, GenerateDesignSystemRequest
from ai.design_system_service import generate_design_system, list_design_systems
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
