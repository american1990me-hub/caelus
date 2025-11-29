from __future__ import annotations

import json
from pathlib import Path

from caelus.ledger.signed_ledger import SignedOmegaLedger
from caelus.cace.omega_bridge import append_cace_receipts_to_ledger


def _load_payloads(path: Path) -> list[dict]:
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    out = []
    for ln in lines:
        data = json.loads(ln)
        payload = data.get("payload", {})
        out.append(payload)
    return out


def test_append_cace_receipts_to_ledger(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_cace.log"
    ledger = SignedOmegaLedger(ledger_path)

    receipts = [
        {
            "op": "CAM",
            "layer_id": "L0",
            "coherence": {"c_W": 0.9, "c_X": 0.8, "c_in": 0.85, "c_out": 0.88, "Delta_c": 0.03},
            "flux": {"J_c_in": 1.0, "J_c_out": 0.9, "div_J_c": 0.1},
            "model": {"S_c_model": 0.0, "policy": {}},
            "residual": {"R_c": 0.01},
            "approx": {"rank_used": {"(0,0)": 4}, "approx_fraction_flops": 0.5},
        }
    ]

    append_cace_receipts_to_ledger(ledger, engine_name="test_engine", receipts=receipts)

    assert ledger.verify_chain()

    payloads = _load_payloads(ledger_path)
    # Genesis + 1 cace_layer
    assert any(p.get("type") == "cace_layer" for p in payloads)
    cace_entries = [p for p in payloads if p.get("type") == "cace_layer"]
    assert len(cace_entries) == 1
    entry = cace_entries[0]
    assert entry["engine"] == "test_engine"
    assert entry["receipt"]["op"] == "CAM"
