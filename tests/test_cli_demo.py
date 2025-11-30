from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_demo_coherence_produces_demo_entries(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_demo.log"

    env = os.environ.copy()
    env["PYTHONPATH"] = "."

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "caelus.cli.main",
            "demo-coherence",
            "--ledger",
            str(ledger_path),
            "--n",
            "32",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
    )
    assert result.returncode == 0, f"demo-coherence failed: {result.stderr}"
    assert ledger_path.exists()

    lines = [ln for ln in ledger_path.read_text().splitlines() if ln.strip()]
    assert len(lines) >= 1 + 4  # genesis + 4 demo entries

    for line in lines[-4:]:
        data = json.loads(line)
        payload = data["payload"]
        assert payload["type"] == "coherence_demo"
        assert "gamma_fd" in payload
        assert "gamma_spec" in payload
