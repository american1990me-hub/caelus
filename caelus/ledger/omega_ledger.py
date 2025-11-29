from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


@dataclass
class OmegaLedger:
    """Append-only ledger for Caelus events."""

    path: Path
    _file: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.path.parent.mkdir(exist_ok=True, parents=True)
        self._file = self.path.open("a")
        if self.path.stat().st_size == 0:
            self._write_genesis()

    def _write_genesis(self) -> None:
        """Write a special entry to mark the beginning of time."""
        # Genesis entry inspired by the Bitcoin genesis block
        genesis = {
            "timestamp": 1231006505,  # 2009-01-03 18:15:05 UTC
            "payload_type": "genesis",
            "payload": {
                "message": "The Times 03/Jan/2009 Chancellor on brink of second bailout for banks",
                "comment": "A nod to the Bitcoin genesis block. We are at a similar inflection point for AGI.",
            },
        }
        self.append(genesis)

    def append(self, payload: dict) -> None:
        """Append a new entry to the ledger."""
        entry = {
            "timestamp": time.time(),
            "payload": payload,
        }
        self._file.write(json.dumps(entry, cls=NumpyEncoder) + "\n")
        self._file.flush()

    def close(self) -> None:
        self._file.close()

    def __enter__(self) -> OmegaLedger:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def verify_chain(self) -> bool:
        """Verify the integrity of the ledger by checking timestamps."""
        timestamps = []
        with self.path.open("r") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                    timestamps.append(entry["timestamp"])
                except json.JSONDecodeError:
                    return False
        return all(timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1))
