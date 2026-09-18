from ai.design_system import (
    DesignColors,
    DesignGrid,
    DesignMotion,
    DesignRadius,
    DesignResponsive,
    DesignSpacing,
    DesignSystem,
    DesignTypography,
    DesignVisual,
)
from ai.landing_blueprint import LandingBlueprint, MediaPlacement
from ai.landing_blueprint_service import _validate_media_and_sections, compile_render_spec
from ai.layout_plan import LayoutPlan, LayoutSection


def make_blueprint() -> LandingBlueprint:
    system = DesignSystem(
        colors=DesignColors(
            primary="#111111",
            secondary="#222222",
            accent="#C08A45",
            background="#FFFFFF",
            surface="#F7F7F7",
            text="#111111",
            muted="#666666",
            border="#DDDDDD",
        ),
        typography=DesignTypography(
            display="Inter",
            heading="Inter",
            body="Inter",
            label="Inter",
            button="Inter",
        ),
        spacing=DesignSpacing(
            xs="4px",
            sm="8px",
            md="16px",
            lg="24px",
            xl="40px",
            two_xl="64px",
            section="80px",
        ),
        radius=DesignRadius(
            none="0",
            small="4px",
            medium="8px",
            large="16px",
            pill="999px",
        ),
        grid=DesignGrid(
            max_width="1200px",
            columns=12,
            gutter="24px",
            margins="24px",
        ),
        motion=DesignMotion(
            duration="300ms",
            easing="ease-out",
            intensity="LOW",
        ),
        visual=DesignVisual(
            image_treatment="natural",
            shadows="soft",
            borders="subtle",
            overlays="minimal",
        ),
        responsive=DesignResponsive(
            mobile="single-column",
            tablet="two-column",
            desktop="twelve-column",
        ),
    )
    plan = LayoutPlan(
        sections=[
            LayoutSection(
                id="hero",
                purpose="Apresentar o negócio e gerar ação",
                layout="cinematic_fullscreen",
                content_source="landing.hero",
                visual_treatment="hero image",
                interaction="cta",
                motion="fade",
                responsive_behavior="reduzir imagem no mobile",
            )
        ],
        page_rhythm="hero followed by clear proof",
        responsive_strategy="mobile-first",
        accessibility_strategy="semantic structure and visible focus",
        performance_strategy="lazy load non-hero images",
    )
    return LandingBlueprint(
        professional_profile="Diretor de Arte Digital — 20+ anos",
        design_system=system,
        layout_plan=plan,
        media_placements=[
            MediaPlacement(
                image_path="companies/test/gallery/hero.jpg",
                role="hero",
                target_sections=["hero"],
                priority=10,
                treatment="full bleed",
            )
        ],
        content_tone="premium and direct",
        conversion_strategy=["agendamento acima da dobra"],
        confidence=0.9,
        warnings=[],
        missing_data=[],
    )


def test_blueprint_compiles_safe_media_references():
    blueprint = make_blueprint()
    _validate_media_and_sections(
        blueprint,
        {"image_paths": ["companies/test/gallery/hero.jpg"]},
    )
    spec = compile_render_spec({}, blueprint)

    assert spec.sections[0].image_references == ["media.image_01"]
    assert spec.media.bindings[0].reference == "media.image_01"
    assert spec.media.bindings[0].source_path == "companies/test/gallery/hero.jpg"


def test_blueprint_rejects_image_from_another_source():
    blueprint = make_blueprint()
    try:
        _validate_media_and_sections(blueprint, {"image_paths": []})
    except ValueError as exc:
        assert "não pertence" in str(exc)
        return
    raise AssertionError("Expected foreign media to be rejected")
