from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .config import load_config
from .sessions import load_fabric_for_session


router = APIRouter(prefix="/api/metrics", tags=["metrics"])
_cfg = load_config()


@router.get("/gate5/{session_id}")
async def get_gate5_metrics(session_id: str):
    try:
        fabric = load_fabric_for_session(_cfg.omega_dir, session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    conv = fabric.get("conversation_graph", {})
    turns = conv.get("turns", [])

    series = []
    for t in turns:
        attrs = t.get("attributes", {})
        series.append({
            "turn_index": attrs.get("turn_index"),
            "Gamma": attrs.get("Gamma"),
            "C_self": attrs.get("C_self"),
            "DeltaM_repair": attrs.get("DeltaM_repair"),
            "meta": attrs.get("meta", {}),
        })

    series.sort(key=lambda r: (r["turn_index"] if r["turn_index"] is not None else 0))
    return {"session_id": session_id, "turns": series}


@router.get("/cace/{session_id}")
async def get_cace_metrics(session_id: str):
    try:
        fabric = load_fabric_for_session(_cfg.omega_dir, session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")

    learn = fabric.get("learning_graph", {})
    nodes = learn.get("nodes", [])

    layers = []
    summaries = []
    updates = []

    for n in nodes:
        ntype = n.get("node_type")
        attrs = n.get("attributes", {})
        if ntype == "cace_layer":
            layers.append({
                "id": n.get("id"),
                "label": n.get("label"),
                "layer_id": attrs.get("layer_id"),
                "coherence": attrs.get("coherence"),
                "flux": attrs.get("flux"),
                "residual": attrs.get("residual"),
                "approx": attrs.get("approx"),
            })
        elif ntype == "compute_summary":
            summaries.append({
                "id": n.get("id"),
                **attrs,
            })
        elif ntype == "policy_update":
            updates.append({
                "id": n.get("id"),
                **attrs,
            })

    return {
        "session_id": session_id,
        "layers": layers,
        "summaries": summaries,
        "policy_updates": updates,
    }
