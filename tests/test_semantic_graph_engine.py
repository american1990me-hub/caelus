from __future__ import annotations

from caelus.language.intents import Intent, IntentType
from caelus.graphs.semantic import SemanticGraphEngine


def test_semantic_graph_activation_and_edges_for_define() -> None:
    engine = SemanticGraphEngine()
    intent = Intent(
        type=IntentType.DEFINE,
        concepts=["sem:coherence_field", "sem:caelus"],
        targets=["coherence field and Caelus"],
        secondary_concepts=[],
        secondary_targets=[],
    )

    engine.apply_intent(intent)
    snap = engine.snapshot()

    node_ids = {n["id"] for n in snap["nodes"]}
    assert "sem:coherence_field" in node_ids
    assert "sem:caelus" in node_ids

    active = set(snap["active_nodes"])
    assert "sem:coherence_field" in active
    assert "sem:caelus" in active

    relations = {(e["source"], e["target"], e["relation"]) for e in snap["edges"]}
    assert ("sem:coherence_field", "sem:caelus", "related_to") in relations
    assert ("sem:caelus", "sem:coherence_field", "related_to") in relations
