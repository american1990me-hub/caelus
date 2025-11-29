from __future__ import annotations

from caelus.language.noetica_interpreter import interpret
from caelus.language.intents import IntentType


def test_define_coherence_maps_to_define_intent_and_concept() -> None:
    u = interpret("define coherence field")
    assert u.intent.type == IntentType.DEFINE
    assert "sem:coherence_field" in u.intent.concepts


def test_compare_caelus_and_noetica_detects_compare_intent() -> None:
    u = interpret("compare Caelus and Noetica")
    assert u.intent.type == IntentType.COMPARE
    assert "sem:caelus" in u.intent.concepts
    assert "sem:noetica" in u.intent.secondary_concepts


def test_rigor_modifier_detected() -> None:
    u = interpret("be more rigorous about coherence")
    assert u.intent.type == IntentType.RIGOR
    # Still picks up concepts
    assert "sem:coherence_field" in u.intent.concepts
