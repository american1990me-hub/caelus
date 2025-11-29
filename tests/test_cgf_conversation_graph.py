from __future__ import annotations

import json
from pathlib import Path

from caelus.conversation.testing import run_scenario_with_metrics
from caelus.ledger.signed_ledger import SignedOmegaLedger
from caelus.cgf.from_omega import build_fabric_from_omega


def _load_payloads(path: Path) -> list[dict]:
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    out = []
    for ln in lines:
        data = json.loads(ln)
        payload = data.get("payload", {})
        out.append(payload)
    return out


def test_conversation_graph_from_omega(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_conv_cgf.log"
    ledger = SignedOmegaLedger(ledger_path)

    # run a scenario with Ω logging
    _ = run_scenario_with_metrics(
        "tests/fixtures/conv_scenarios/noetica_mix.json",
        ledger=ledger,
        session_id="noetica_sess_1",
    )

    fabric = build_fabric_from_omega(ledger_path, fabric_id="fabric_conv_test")
    d = fabric.to_dict()

    conv = d["conversation_graph"]
    sessions = conv["sessions"]
    turns = conv["turns"]

    assert len(sessions) >= 1
    assert len(turns) >= 1

    # Check that at least one turn node carries Noetica-related metadata
    has_noetica = False
    for t in turns:
        meta = t["attributes"].get("meta", {})
        word = meta.get("word")
        if word in {"coherare", "glyphos"}:
            has_noetica = True
            break
    assert has_noetica
