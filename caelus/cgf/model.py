from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List

@dataclass
class GraphNode:
    id: str
    label: str
    graph_type: str
    node_type: str
    attributes: Dict[str, Any]

@dataclass
class GraphEdge:
    id: str
    graph_type: str
    source: str
    target: str
    edge_type: str
    attributes: Dict[str, Any]

@dataclass
class StateGraph:
    id: str = "state"
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class ProcessGraph:
    id: str = "process"
    states: List[GraphNode] = field(default_factory=list)
    transitions: List[GraphEdge] = field(default_factory=list)

@dataclass
class ArgumentGraph:
    id: str = "argument"
    claims: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class LearningGraph:
    id: str = "learning"
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class ConstraintGraph:
    id: str = "constraint"
    variables: List[GraphNode] = field(default_factory=list)
    constraints: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class ProbabilisticGraph:
    id: str = "probabilistic"
    random_variables: List[GraphNode] = field(default_factory=list)
    factors: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class SemanticGraph:
    id: str = "semantic"
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class ConversationGraph:
    id: str = "conv"
    sessions: List[GraphNode] = field(default_factory=list)
    turns: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)

@dataclass
class CaelusGraphFabric:
    id: str
    version: str
    omega_ledger_payloads: List[Dict[str, Any]]
    state_graph: StateGraph
    process_graph: ProcessGraph
    argument_graph: ArgumentGraph
    learning_graph: LearningGraph
    constraint_graph: ConstraintGraph = field(default_factory=ConstraintGraph)
    probabilistic_graph: ProbabilisticGraph = field(default_factory=ProbabilisticGraph)
    semantic_graph: SemanticGraph = field(default_factory=SemanticGraph)
    conversation_graph: ConversationGraph = field(default_factory=ConversationGraph)  # NEW
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "version": self.version,
            "omega_ledger_payloads": list(self.omega_ledger_payloads),
            "state_graph": {
                "id": self.state_graph.id,
                "nodes": [asdict(n) for n in self.state_graph.nodes],
                "edges": [asdict(e) for e in self.state_graph.edges],
            },
            "process_graph": {
                "id": self.process_graph.id,
                "states": [asdict(n) for n in self.process_graph.states],
                "transitions": [asdict(e) for e in self.process_graph.transitions],
            },
            "argument_graph": {
                "id": self.argument_graph.id,
                "claims": [asdict(n) for n in self.argument_graph.claims],
                "edges": [asdict(e) for e in self.argument_graph.edges],
            },
            "learning_graph": {
                "id": self.learning_graph.id,
                "nodes": [asdict(n) for n in self.learning_graph.nodes],
                "edges": [asdict(e) for e in self.learning_graph.edges],
            },
            "constraint_graph": {
                "id": self.constraint_graph.id,
                "variables": [asdict(n) for n in self.constraint_graph.variables],
                "constraints": [asdict(n) for n in self.constraint_graph.constraints],
                "edges": [asdict(e) for e in self.constraint_graph.edges],
            },
            "probabilistic_graph": {
                "id": self.probabilistic_graph.id,
                "random_variables": [asdict(n) for n in self.probabilistic_graph.random_variables],
                "factors": [asdict(n) for n in self.probabilistic_graph.factors],
                "edges": [asdict(e) for e in self.probabilistic_graph.edges],
            },
            "semantic_graph": {
                "id": self.semantic_graph.id,
                "nodes": [asdict(n) for n in self.semantic_graph.nodes],
                "edges": [asdict(e) for e in self.semantic_graph.edges],
            },
            "conversation_graph": {
                "id": self.conversation_graph.id,
                "sessions": [asdict(n) for n in self.conversation_graph.sessions],
                "turns": [asdict(n) for n in self.conversation_graph.turns],
                "edges": [asdict(e) for e in self.conversation_graph.edges],
            },
            "metadata": dict(self.metadata),
        }
