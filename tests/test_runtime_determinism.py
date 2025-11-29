from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig
from caelus.ledger.signed_ledger import SignedOmegaLedger
from caelus.agent.sensory import reset_sensory_engines


class FakeTimer:
    def __init__(self, start_time: float = 1704067200.0) -> None:
        self._it = self._timer(start_time)

    def __call__(self) -> float:
        return next(self._it)

    def _timer(self, start_time: float) -> Iterator[float]:
        t = start_time
        while True:
            yield t
            t += 1.0


def _read_chain_hashes(path: Path) -> list[str]:
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    hashes: list[str] = []
    for ln in lines:
        data = json.loads(ln)
        hashes.append(data["chain_hash"])
    return hashes


def test_runtime_determinism_same_seed_same_chain(tmp_path: Path) -> None:
    reset_sensory_engines()
    ledger_path = tmp_path / "omega_session.log"
    context_path = tmp_path / "context.json"
    policy_path = tmp_path / "policy.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=2,
        seed=42,
        ledger_path=ledger_path,
        time_source=FakeTimer(),
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    # First run
    rt.run_session("hello world")
    hashes_1 = _read_chain_hashes(ledger_path)

    # Reset file and run again with same config
    reset_sensory_engines()
    ledger_path.unlink()
    if context_path.exists():
        context_path.unlink()
    if policy_path.exists():
        policy_path.unlink()

    cfg.time_source = FakeTimer()  # Reset timer
    rt2 = CaelusRuntime(cfg)
    rt2.run_session("hello world")
    hashes_2 = _read_chain_hashes(ledger_path)

    assert hashes_1 == hashes_2


def test_runtime_determinism_diff_seed_diff_chain(tmp_path: Path) -> None:
    reset_sensory_engines()
    ledger_path1 = tmp_path / "omega_session1.log"
    ledger_path2 = tmp_path / "omega_session2.log"

    cfg1 = CaelusRuntimeConfig(
        grid_size=16, steps=2, seed=1, ledger_path=ledger_path1, time_source=FakeTimer()
    )
    cfg2 = CaelusRuntimeConfig(
        grid_size=16, steps=2, seed=2, ledger_path=ledger_path2, time_source=FakeTimer()
    )

    rt1 = CaelusRuntime(cfg1)
    rt2 = CaelusRuntime(cfg2)

    rt1.run_session("same text")

    reset_sensory_engines()
    rt2.run_session("same text")

    hashes_1 = _read_chain_hashes(ledger_path1)
    hashes_2 = _read_chain_hashes(ledger_path2)

    assert hashes_1 != hashes_2
