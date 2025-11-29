from __future__ import annotations

from caelus.language.intents import Intent, IntentType
from caelus.graphs.semantic import SemanticGraphEngine
from caelus.graphs.argument import ArgumentGraphEngine
from caelus.response.plan import make_response_plan, ResponseMode


def test_make_response_plan_definition() -> None:
    intent = Intent(
        type=IntentType.DEFINE,
        concepts=["sem:coherence_field"],
        targets=["coherence field"],
        secondary_concepts=[],
        secondary_targets=[],
    )
    sem_engine = SemanticGraphEngine()
    arg_engine = ArgumentGraphEngine()

    plan = make_response_plan(intent, sem_engine, arg_engine)

    assert plan.mode == ResponseMode.DEFINITION
    assert plan.focus_concepts == ["sem:coherence_field"]
    assert plan.rigor_level == 0
    assert plan.creative_level == 0


def test_make_response_plan_comparison_min_two_concepts() -> None:
    intent = Intent(
        type=IntentType.COMPARE,
        concepts=["sem:caelus"],
        targets=["Caelus"],
        secondary_concepts=["sem:noetica"],
        secondary_targets=["Noetica"],
    )
    sem_engine = SemanticGraphEngine()
    arg_engine = ArgumentGraphEngine()

    plan = make_response_plan(intent, sem_engine, arg_engine)

    assert plan.mode == ResponseMode.COMPARISON
    assert "sem:caelus" in plan.focus_concepts
    assert "sem:noetica" in plan.focus_concepts


def test_make_response_plan_rigor_modifier() -> None:
    intent = Intent(
        type=IntentType.RIGOR,
        concepts=["sem:coherence_field"],
        targets=["be more rigorous about coherence field"],
        secondary_concepts=[],
        secondary_targets=[],
    )
    sem_engine = SemanticGraphEngine()
    arg_engine = ArgumentGraphEngine()

    plan = make_response_plan(intent, sem_engine, arg_engine)

    assert plan.mode == ResponseMode.MODIFIER_ONLY
    assert plan.rigor_level == 1
    assert plan.creative_level == 0
