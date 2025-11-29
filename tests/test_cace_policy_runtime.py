from __future__ import annotations

import json
from pathlib import Path

from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig


def _load_payloads(path: Path) -> list[dict]:
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    out = []
    for ln in lines:
        data = json.loads(ln)
        payload = data.get("payload", {})
        out.append(payload)
    return out


def test_runtime_writes_cace_policy_update(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_policy.log"
    context_path = tmp_path / "ctx_policy.json"
    policy_path = tmp_path / "policy.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=321,
        ledger_path=ledger_path,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    reply = rt.run_session("define coherence field")
    assert isinstance(reply, str)
    assert rt.last_policy_record is not None

    payloads = _load_payloads(ledger_path)
    has_policy_update = any(p.get("type") == "cace_policy_update" for p in payloads)
    assert has_policy_update


def test_policy_file_created_and_updated(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_policy2.log"
    context_path = tmp_path / "ctx_policy2.json"
    policy_path = tmp_path / "policy2.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=777,
        ledger_path=ledger_path,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    _ = rt.run_session("compare Caelus and Noetica")

    assert policy_path.exists()
    data = json.loads(policy_path.read_text())
    assert "rank_max" in data
    assert "tau_high" in data
    assert "tau_mid" in data
