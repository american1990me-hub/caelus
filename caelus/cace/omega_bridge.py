from __future__ import annotations

from typing import List, Dict, Any

from ..ledger.signed_ledger import SignedOmegaLedger
from .runtime_model import ComputeCoherenceSnapshot


def append_cace_receipts_to_ledger(
    ledger: SignedOmegaLedger,
    engine_name: str,
    receipts: List[Dict[str, Any]],
) -> None:
    """Append each CACE receipt as a signed Ω-ledger entry."""
    for rec in receipts:
        payload = {
            "type": "cace_layer",
            "engine": engine_name,
            "receipt": rec,
        }
        ledger.append(payload)


def append_compute_snapshot_to_ledger(
    ledger: SignedOmegaLedger,
    engine_name: str,
    snap: ComputeCoherenceSnapshot,
) -> None:
    """Append a summarized compute coherence snapshot into the Ω-ledger."""
    payload = {
        "type": "compute_coherence_summary",
        "engine": engine_name,
        "summary": {
            "mean_c_in": snap.mean_c_in,
            "mean_c_out": snap.mean_c_out,
            "max_abs_R_c": snap.max_abs_R_c,
            "num_layers": snap.num_layers,
        },
    }
    ledger.append(payload)
