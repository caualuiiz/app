"""AI Digital Art Director design routes — Phase 2.1."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from auth import require_roles
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
