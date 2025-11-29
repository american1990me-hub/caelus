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


def test_runtime_logs_cace_layers_and_summary(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_cace_runtime.log"
    context_path = tmp_path / "ctx_cace_runtime.json"
    policy_path = tmp_path / "policy_cace_runtime.json"

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
    assert rt.last_compute_snapshot is not None
    snap = rt.last_compute_snapshot
    assert snap.num_layers >= 1
    assert 0.0 <= snap.mean_c_in <= 1.0
    assert 0.0 <= snap.mean_c_out <= 1.0

    payloads = _load_payloads(ledger_path)
    has_cace_layer = any(p.get("type") == "cace_layer" for p in payloads)
    has_summary = any(p.get("type") == "compute_coherence_summary" for p in payloads)
    assert has_cace_layer
    assert has_summary


def test_cace_runtime_deterministic(tmp_path: Path) -> None:
    ledger1 = tmp_path / "omega_cace_rt1.log"
    ledger2 = tmp_path / "omega_cace_rt2.log"
    ctx1 = tmp_path / "ctx_cace_rt1.json"
    ctx2 = tmp_path / "ctx_cace_rt2.json"
    policy1 = tmp_path / "policy_cace_rt1.json"
    policy2 = tmp_path / "policy_cace_rt2.json"

    cfg1 = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=999,
        ledger_path=ledger1,
        context_path=ctx1,
        policy_path=policy1,
    )
    cfg2 = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=999,
        ledger_path=ledger2,
        context_path=ctx2,
        policy_path=policy2,
    )
    rt1 = CaelusRuntime(cfg1)
    rt2 = CaelusRuntime(cfg2)

    _ = rt1.run_session("compare Caelus and Noetica")
    _ = rt2.run_session("compare Caelus and Noetica")

    snap1 = rt1.last_compute_snapshot
    snap2 = rt2.last_compute_snapshot
    assert snap1 is not None and snap2 is not None

    assert snap1.num_layers == snap2.num_layers
    assert snap1.mean_c_in == snap2.mean_c_in
    assert snap1.mean_c_out == snap2.mean_c_out
    assert snap1.max_abs_R_c == snap2.max_abs_R_c
