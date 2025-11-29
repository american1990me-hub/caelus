from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set

from ..language.intents import Intent


@dataclass
class SemanticNode:
    id: str
    label: str
    # Optional metadata; we keep it simple for now.
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class SemanticEdge:
    source: str
    target: str
    relation: str  # e.g. "related_to", "defined_with", "compared_to"


@dataclass
class SemanticGraph:
    nodes: Dict[str, SemanticNode] = field(default_factory=dict)
    edges: List[SemanticEdge] = field(default_factory=list)
    active_nodes: Set[str] = field(default_factory=set)

    def ensure_node(self, cid: str) -> SemanticNode:
        if cid not in self.nodes:
            self.nodes[cid] = SemanticNode(id=cid, label=cid)
        return self.nodes[cid]

    def add_edge(self, source: str, target: str, relation: str) -> None:
        self.edges.append(SemanticEdge(source=source, target=target, relation=relation))

    def activate(self, concept_ids: List[str]) -> None:
        for cid in concept_ids:
            if cid in self.nodes:
                self.active_nodes.add(cid)

    def deactivate_all(self) -> None:
        self.active_nodes.clear()


@dataclass
class SemanticGraphEngine:
    graph: SemanticGraph = field(default_factory=SemanticGraph)

    def apply_intent(self, intent: Intent) -> None:
        """Update the semantic graph in response to an Intent.

        Rules:
        - DEFINE / EXPLAIN / WHY → ensure nodes, connect them with "related_to".
        - COMPARE → ensure nodes for primary/secondary and connect them with "compared_to".
        - RIGOR / CREATIVE / UNKNOWN → treat as context; activate any mentioned concepts.
        """
        # Ensure nodes exist for all concepts
        all_concepts = list(intent.concepts) + list(intent.secondary_concepts)
        for cid in all_concepts:
            self.graph.ensure_node(cid)

        if intent.type.name in {"DEFINE", "EXPLAIN", "WHY"}:
            # For multiple primary concepts, relate them pairwise.
            prim = list(intent.concepts)
            for i in range(len(prim)):
                for j in range(i + 1, len(prim)):
                    self.graph.add_edge(prim[i], prim[j], relation="related_to")
                    self.graph.add_edge(prim[j], prim[i], relation="related_to")

        if intent.type.name == "COMPARE":
            for pc in intent.concepts:
                for sc in intent.secondary_concepts:
                    self.graph.add_edge(pc, sc, relation="compared_to")
                    self.graph.add_edge(sc, pc, relation="compared_to")

        # Activate all mentioned concepts for context
        self.graph.deactivate_all()
        self.graph.activate(all_concepts)

    def snapshot(self) -> dict:
        return {
            "nodes": [
                {"id": n.id, "label": n.label, "metadata": n.metadata}
                for n in self.graph.nodes.values()
            ],
            "edges": [
                {"source": e.source, "target": e.target, "relation": e.relation}
                for e in self.graph.edges
            ],
            "active_nodes": sorted(self.graph.active_nodes),
        }
