from __future__ import annotations

from caelus.response.plan import ResponsePlan, ResponseMode
from caelus.response.templates import render_response


def test_render_definition_coherence_field_contains_key_phrases() -> None:
    plan = ResponsePlan(
        mode=ResponseMode.DEFINITION,
        focus_concepts=["sem:coherence_field"],
        secondary_concepts=[],
        rigor_level=1,
        creative_level=1,
    )

    text = render_response(plan)
    assert "coherence field" in text.lower()
    assert "Γ" in text or "Gamma" in text  # math flavour


def test_render_comparison_caelus_noetica_mentions_both_and_difference() -> None:
    plan = ResponsePlan(
        mode=ResponseMode.COMPARISON,
        focus_concepts=["sem:caelus", "sem:noetica"],
        secondary_concepts=[],
        rigor_level=0,
        creative_level=0,
    )

    text = render_response(plan)
    lower = text.lower()
    assert "caelus" in lower
    assert "noetica" in lower
    assert "similar" in lower or "both" in lower
    assert "differ" in lower or "difference" in lower


def test_render_modifier_only_rigor_message() -> None:
    plan = ResponsePlan(
        mode=ResponseMode.MODIFIER_ONLY,
        focus_concepts=[],
        secondary_concepts=[],
        rigor_level=1,
        creative_level=0,
    )

    text = render_response(plan)
    assert "rigor" in text.lower()
