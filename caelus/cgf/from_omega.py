from typing import Any, Dict, List, Set
from pathlib import Path
import json

from .model import (
    CaelusGraphFabric,
    StateGraph,
    ProcessGraph,
    ArgumentGraph,
    LearningGraph,
    ConversationGraph,
    GraphNode,
    GraphEdge,
)

def build_conversation_graph_from_payloads(payloads: List[Dict[str, Any]]) -> ConversationGraph:
    sessions: List[GraphNode] = []
    turns: List[GraphNode] = []
    edges: List[GraphEdge] = []

    # Track sessions we have nodes for
    session_nodes: Dict[str, str] = {}
    turn_idx = 0
    edge_idx = 0

    # First pass: find all session_ids
    session_ids: Set[str] = set()
    for p in payloads:
        if p.get("type") in {"conversation_turn_metric", "conversation_summary"}:
            sid = p.get("session_id")
            if isinstance(sid, str):
                session_ids.add(sid)

    # Create a node per session
    for i, sid in enumerate(sorted(session_ids)):
        node_id = f"conv_session_{i}"
        session_nodes[sid] = node_id
        sessions.append(
            GraphNode(
                id=node_id,
                label=f"Conversation session {i}",
                graph_type="conv",
                node_type="conversation_session",
                attributes={"session_id": sid},
            )
        )

    # Second pass: create turn nodes and edges
    turns_for_session: Dict[str, List[str]] = {sid: [] for sid in session_ids}

    for p in payloads:
        ptype = p.get("type")
        if ptype == "conversation_turn_metric":
            sid = p.get("session_id")
            if sid not in session_nodes:
                continue
            node_id = f"conv_turn_{turn_idx}"
            turn_idx += 1

            attrs = {
                "scenario": p.get("scenario"),
                "turn_index": p.get("turn_index"),
                "Gamma": p.get("Gamma"),
                "C_self": p.get("C_self"),
                "DeltaM_repair": p.get("DeltaM_repair"),
                "meta": p.get("meta"),
            }
            turns.append(
                GraphNode(
                    id=node_id,
                    label=f"Turn {attrs['turn_index']} (session {sid})",
                    graph_type="conv",
                    node_type="conversation_turn",
                    attributes=attrs,
                )
            )
            turns_for_session[sid].append(node_id)

    # Edges: session → first turn, and turn → next turn
    for sid, turn_ids in turns_for_session.items():
        if not turn_ids:
            continue
        sess_node_id = session_nodes[sid]
        # session → first turn
        edges.append(
            GraphEdge(
                id=f"conv_edge_{edge_idx}",
                graph_type="conv",
                source=sess_node_id,
                target=turn_ids[0],
                edge_type="session_to_turn",
                attributes={},
            )
        )
        edge_idx += 1

        # chain turns
        for i in range(len(turn_ids) - 1):
            edges.append(
                GraphEdge(
                    id=f"conv_edge_{edge_idx}",
                    graph_type="conv",
                    source=turn_ids[i],
                    target=turn_ids[i + 1],
                    edge_type="turn_to_turn",
                    attributes={},
                )
            )
            edge_idx += 1

    return ConversationGraph(sessions=sessions, turns=turns, edges=edges)

def build_fabric_from_omega(ledger_path: Path, fabric_id: str, version: str = "1.0") -> CaelusGraphFabric:
    """Build a CaelusGraphFabric from a SignedOmegaLedger file."""
    payloads = []
    with ledger_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                payloads.append(json.loads(line)["payload"])
            except (json.JSONDecodeError, KeyError):
                pass

    # For now, we are just building the conversation graph
    state_graph = StateGraph()
    process_graph = ProcessGraph()
    argument_graph = ArgumentGraph()
    learning_graph = LearningGraph()
    conversation_graph = build_conversation_graph_from_payloads(payloads)

    fabric = CaelusGraphFabric(
        id=fabric_id,
        version=version,
        omega_ledger_payloads=payloads,
        state_graph=state_graph,
        process_graph=process_graph,
        argument_graph=argument_graph,
        learning_graph=learning_graph,
        conversation_graph=conversation_graph,
        metadata={"source_ledger": str(ledger_path)},
    )

    return fabric
