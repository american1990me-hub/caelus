from __future__ import annotations

import json
from pathlib import Path

from caelus.conversation.testing import run_scenario_with_metrics
from caelus.ledger.signed_ledger import SignedOmegaLedger


def _load_payloads(path: Path) -> list[dict]:
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    out = []
    for ln in lines:
        data = json.loads(ln)
        payload = data.get("payload", {})
        out.append(payload)
    return out


def test_conversation_metrics_logged_to_omega(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_conv.log"
    ledger = SignedOmegaLedger(ledger_path)

    # use basic scenario
    metrics = run_scenario_with_metrics(
        "tests/fixtures/conv_scenarios/basic_small_talk.json",
        ledger=ledger,
        session_id="test_session_1",
    )

    assert metrics

    payloads = _load_payloads(ledger_path)
    types = {p.get("type", "") for p in payloads}

    assert "conversation_turn_metric" in types
    assert "conversation_summary" in types
