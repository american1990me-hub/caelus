from __future__ import annotations

from pathlib import Path

from caelus.context.dialogue import DialogueContext, save_context, load_context
from caelus.language.intents import Intent, IntentType


def test_rigor_bias_accumulates_and_decays() -> None:
    ctx = DialogueContext()

    # First rigor request
    intent_r1 = Intent(
        type=IntentType.RIGOR,
        concepts=["sem:coherence_field"],
        targets=["be more rigorous about coherence field"],
        secondary_concepts=[],
        secondary_targets=[],
    )
    ctx.apply_intent(intent_r1)
    assert ctx.rigor_bias == 1

    # Second rigor request
    ctx.apply_intent(intent_r1)
    assert ctx.rigor_bias == 2

    # Non-rigor intent should cause gentle decay
    intent_def = Intent(
        type=IntentType.DEFINE,
        concepts=["sem:coherence_field"],
        targets=["define coherence field"],
        secondary_concepts=[],
        secondary_targets=[],
    )
    ctx.apply_intent(intent_def)
    assert ctx.rigor_bias == 1


def test_context_persistence_round_trip(tmp_path: Path) -> None:
    ctx = DialogueContext(rigor_bias=2, creative_bias=1, last_concepts=["sem:caelus"], last_mode="DEFINE")
    path = tmp_path / "ctx.json"
    save_context(path, ctx)

    ctx2 = load_context(path)
    assert ctx2.rigor_bias == 2
    assert ctx2.creative_bias == 1
    assert ctx2.last_concepts == ["sem:caelus"]
