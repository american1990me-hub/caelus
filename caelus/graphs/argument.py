from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from ..language.intents import Intent


@dataclass
class ClaimNode:
    id: str
    text: str
    kind: str  # e.g. "question", "definition_request", "comparison_request"


@dataclass
class ArgumentEdge:
    source: str
    target: str
    relation: str  # e.g. "asks_about", "compares", "refines"


@dataclass
class ArgumentGraph:
    nodes: Dict[str, ClaimNode] = field(default_factory=dict)
    edges: List[ArgumentEdge] = field(default_factory=list)
    _next_id: int = 0

    def new_claim_id(self) -> str:
        self._next_id += 1
        return f"claim:{self._next_id}"


@dataclass
class ArgumentGraphEngine:
    graph: ArgumentGraph = field(default_factory=ArgumentGraph)

    def add_intent_as_claim(self, intent: Intent, raw_text: str) -> str:
        """Add a claim node representing the user's intent.

        Returns the new claim ID.
        """
        kind = self._kind_for_intent(intent)
        cid = self.graph.new_claim_id()
        node = ClaimNode(id=cid, text=raw_text, kind=kind)
        self.graph.nodes[cid] = node

        # Add edges to concept ids as "asks_about" or "compares"
        if intent.type.name in {"DEFINE", "EXPLAIN", "WHY"}:
            for c in intent.concepts:
                self.graph.edges.append(
                    ArgumentEdge(source=cid, target=c, relation="asks_about")
                )
        if intent.type.name == "COMPARE":
            for c in intent.concepts:
                self.graph.edges.append(
                    ArgumentEdge(source=cid, target=c, relation="compares")
                )
            for c in intent.secondary_concepts:
                self.graph.edges.append(
                    ArgumentEdge(source=cid, target=c, relation="compares")
                )

        return cid

    def _kind_for_intent(self, intent: Intent) -> str:
        t = intent.type.name
        if t == "DEFINE":
            return "definition_request"
        if t == "EXPLAIN":
            return "explanation_request"
        if t == "WHY":
            return "why_request"
        if t == "COMPARE":
            return "comparison_request"
        if t == "RIGOR":
            return "rigor_modifier"
        if t == "CREATIVE":
            return "creativity_modifier"
        return "generic"

    def snapshot(self) -> dict:
        return {
            "nodes": [
                {"id": n.id, "text": n.text, "kind": n.kind}
                for n in self.graph.nodes.values()
            ],
            "edges": [
                {"source": e.source, "target": e.target, "relation": e.relation}
                for e in self.graph.edges
            ],
        }
