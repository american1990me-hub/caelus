from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from caelus.math_core.coherence import CoherenceContract
from caelus.math_core.ufe import UFEStepper
from caelus.agent.loops import CaelusInnerLoop, make_initial_state
from caelus.ledger.omega_ledger import OmegaLedger


def test_inner_loop_writes_valid_ledger(tmp_path: Path) -> None:
    """Run a few inner-loop ticks and check Ω-ledger structure."""
    ledger_path = tmp_path / "omega.log"
    ledger = OmegaLedger(ledger_path)

    contract = CoherenceContract()
    stepper = UFEStepper(contract)
    inner = CaelusInnerLoop(stepper=stepper, contract=contract, ledger=ledger)

    np.random.seed(1234)
    state = make_initial_state((16, 16), contract)

    for _ in range(3):
        state = inner.tick(state, sensory_raw={"text": "hello"})

    assert ledger_path.exists()
    assert ledger.verify_chain() is True

    lines = [ln for ln in ledger_path.read_text().splitlines() if ln.strip()]
    assert len(lines) == 1 + 3  # genesis + 3 ticks

    last = json.loads(lines[-1])
    payload = last["payload"]
    assert payload["type"] == "inner_tick"
    for key in ("C_old", "C_new", "gamma_old", "gamma_new", "dt"):
        assert key in payload
        assert isinstance(payload[key], (int, float))


def test_cli_run_produces_ledger(tmp_path: Path) -> None:
    """Run the CLI and ensure it creates a ledger file with ticks."""
    ledger_path = tmp_path / "omega_cli.log"

    result = subprocess.run(
        [
            sys.executable,  # Use the same python that runs the tests
            "-m",
            "caelus.cli.main",
            "run",
            "--input",
            "hello",
            "--steps",
            "2",
            "--ledger",
            str(ledger_path),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0, f"CLI failed: {result.stderr}"
    assert ledger_path.exists(), "CLI did not create ledger file"

    lines = [ln for ln in ledger_path.read_text().splitlines() if ln.strip()]
    assert len(lines) >= 2  # genesis + at least 1 tick
    last = json.loads(lines[-1])
    assert last["payload"]["type"] == "inner_tick"
