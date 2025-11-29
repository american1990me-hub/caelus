from __future__ import annotations

import json
from pathlib import Path

from caelus.ledger.signed_ledger import SignedOmegaLedger


def test_signed_ledger_detects_tampering(tmp_path: Path) -> None:
    ledger_path = tmp_path / "omega_signed.log"
    ledger = SignedOmegaLedger(ledger_path)

    # Append a couple of entries
    ledger.append({"type": "test", "value": 1})
    ledger.append({"type": "test", "value": 2})

    # Initially the chain should verify
    assert ledger.verify_chain() is True

    # Tamper with the middle entry's payload
    lines = [ln for ln in ledger_path.read_text().splitlines() if ln.strip()]
    assert len(lines) == 3  # genesis + 2

    tampered = json.loads(lines[1])
    tampered["payload"]["value"] = 999  # corrupt
    lines[1] = json.dumps(tampered, separators=(",", ":"), sort_keys=True)

    ledger_path.write_text("\n".join(lines) + "\n")

    # Now verification must fail
    ledger2 = SignedOmegaLedger(ledger_path)
    assert ledger2.verify_chain() is False
