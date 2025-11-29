from __future__ import annotations

from caelus.language.intents import Intent, IntentType
from caelus.graphs.argument import ArgumentGraphEngine


def test_argument_graph_adds_claim_and_edges() -> None:
    engine = ArgumentGraphEngine()
    intent = Intent(
        type=IntentType.COMPARE,
        concepts=["sem:caelus"],
        targets=["Caelus"],
        secondary_concepts=["sem:noetica"],
        secondary_targets=["Noetica"],
    )

    claim_id = engine.add_intent_as_claim(intent, raw_text="compare Caelus and Noetica")

    snap = engine.snapshot()
    node_ids = {n["id"] for n in snap["nodes"]}
    assert claim_id in node_ids

    edges = snap["edges"]
    rels = {(e["source"], e["target"], e["relation"]) for e in edges}

    assert (claim_id, "sem:caelus", "compares") in rels
    assert (claim_id, "sem:noetica", "compares") in rels
