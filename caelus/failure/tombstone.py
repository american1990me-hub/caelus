from __future__ import annotations

import os
import traceback
from dataclasses import dataclass
from typing import Any

from ..ledger.signed_ledger import SignedOmegaLedger


@dataclass
class TombstoneReporter:
    ledger: SignedOmegaLedger

    def report(self, exit_reason: str, gamma: float | None = None, extra: dict[str, Any] | None = None) -> None:
        payload: dict[str, Any] = {
            "type": "tombstone",
            "exit": exit_reason,
            "disk_MB": self._disk_free_mb(),
            "traceback": traceback.format_exc(),
        }
        if gamma is not None:
            payload["gamma"] = gamma
        if extra:
            payload.update(extra)
        self.ledger.append(payload)

    def _disk_free_mb(self) -> float:
        st = os.statvfs(".")
        return st.f_bavail * st.f_frsize / (1024 * 1024)
