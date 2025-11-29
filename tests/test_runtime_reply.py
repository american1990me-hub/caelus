from __future__ import annotations

import json
from pathlib import Path

from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig


def _find_reply_entry(ledger_path: Path) -> dict | None:
    lines = [ln for ln in ledger_path.read_text().splitlines() if ln.strip()]
    for ln in lines:
        data = json.loads(ln)
        payload = data.get("payload", {})
        if payload.get("type") == "reply":
            return payload
    return None


def test_runtime_generates_definition_reply_and_logs_plan(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_reply.log"
    context_path = tmp_path / "ctx_reply.json"
    policy_path = tmp_path / "policy_reply.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=123,
        ledger_path=ledger_path,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    reply = rt.run_session("define coherence field")

    assert isinstance(reply, str)
    assert "coherence field" in reply.lower()

    reply_entry = _find_reply_entry(ledger_path)
    assert reply_entry is not None

    plan = reply_entry["plan"]
    assert plan["mode"] == "DEFINITION"


def test_runtime_generates_comparison_reply(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_reply_cmp.log"
    context_path = tmp_path / "ctx_reply_cmp.json"
    policy_path = tmp_path / "policy_reply_cmp.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=123,
        ledger_path=ledger_path,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    reply = rt.run_session("compare Caelus and Noetica")

    assert "caelus" in reply.lower()
    assert "noetica" in reply.lower()

    reply_entry = _find_reply_entry(ledger_path)
    assert reply_entry is not None
    plan = reply_entry["plan"]
    assert plan["mode"] == "COMPARISON"
