from __future__ import annotations

from typing import Any, Dict, List

from ..ledger.signed_ledger import SignedOmegaLedger
from .metrics import TurnMetrics


def append_turn_metrics_to_ledger(
    ledger: SignedOmegaLedger,
    session_id: str,
    scenario_name: str,
    turn_metrics: TurnMetrics,
) -> None:
    """Append a single Gate-5 metrics record into the Ω-ledger.

    Payload type: "conversation_turn_metric".
    """
    payload: Dict[str, Any] = {
        "type": "conversation_turn_metric",
        "session_id": session_id,
        "scenario": scenario_name,
        "turn_index": turn_metrics.turn_index,
        "Gamma": turn_metrics.Gamma,
        "C_self": turn_metrics.C_self,
        "DeltaM_repair": turn_metrics.DeltaM_repair,
        "meta": dict(turn_metrics.meta),
    }
    ledger.append(payload)


def append_conversation_summary(
    ledger: SignedOmegaLedger,
    session_id: str,
    scenario_name: str,
    metrics_log: List[TurnMetrics],
) -> None:
    """Append a summary record for a whole scripted conversation.

    Payload type: "conversation_summary".
    """
    if not metrics_log:
        return

    g_values = [tm.Gamma for tm in metrics_log]
    c_values = [tm.C_self for tm in metrics_log]
    d_values = [tm.DeltaM_repair for tm in metrics_log]

    payload: Dict[str, Any] = {
        "type": "conversation_summary",
        "session_id": session_id,
        "scenario": scenario_name,
        "num_turns": len(metrics_log),
        "Gamma_final": g_values[-1],
        "Gamma_min": min(g_values),
        "C_self_min": min(c_values),
        "DeltaM_max": max(d_values),
    }
    ledger.append(payload)
