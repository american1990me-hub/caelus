from __future__ import annotations

import json
import time
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .keys import OmegaKeyPair, load_keypair, sign_bytes, verify_signature


class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, np.ndarray):
            return o.tolist()
        return super().default(o)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class SignedOmegaEntry:
    index: int
    prev_hash: str
    timestamp: float
    payload: dict[str, Any]
    hash: str
    chain_hash: str
    signature_hex: str

    def to_json(self) -> str:
        return json.dumps(asdict(self), separators=(",", ":"), sort_keys=True, cls=NumpyJSONEncoder)


@dataclass
class SignedOmegaLedger:
    path: Path
    keypair: OmegaKeyPair | None = None
    time_source: Callable[[], float] = time.time

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.keypair is None:
            self.keypair = load_keypair()
        if not self.path.exists():
            self._init_genesis()

    # --- low-level helpers ---

    def _compute_entry_hash(self, index: int, prev_hash: str, timestamp: float, payload: dict[str, Any]) -> str:
        body = {
            "index": index,
            "prev_hash": prev_hash,
            "timestamp": timestamp,
            "payload": payload,
        }
        return sha256_hex(json.dumps(body, separators=(",", ":"), sort_keys=True, cls=NumpyJSONEncoder).encode())

    def _compute_chain_hash(self, prev_chain_hash: str, entry_hash: str) -> str:
        return sha256_hex((prev_chain_hash + entry_hash).encode())

    def _last_entry(self) -> SignedOmegaEntry:
        with self.path.open() as f:
            last_line = list(f)[-1]
        data = json.loads(last_line)
        return SignedOmegaEntry(**data)

    def _init_genesis(self) -> None:
        timestamp = self.time_source()
        payload = {"genesis": True}
        base_hash = self._compute_entry_hash(0, "0" * 64, timestamp, payload)
        chain_hash = self._compute_chain_hash("0" * 64, base_hash)
        assert self.keypair is not None
        sig = sign_bytes(self.keypair, chain_hash.encode())

        genesis = SignedOmegaEntry(
            index=0,
            prev_hash="0" * 64,
            timestamp=timestamp,
            payload=payload,
            hash=base_hash,
            chain_hash=chain_hash,
            signature_hex=sig.hex(),
        )
        with self.path.open("w") as f:
            f.write(genesis.to_json() + "\n")

    # --- public API ---

    def append(self, payload: dict[str, Any]) -> SignedOmegaEntry:
        last = self._last_entry()
        index = last.index + 1
        prev_hash = last.hash
        timestamp = self.time_source()

        entry_hash = self._compute_entry_hash(index, prev_hash, timestamp, payload)
        chain_hash = self._compute_chain_hash(last.chain_hash, entry_hash)

        assert self.keypair is not None
        sig = sign_bytes(self.keypair, chain_hash.encode())

        entry = SignedOmegaEntry(
            index=index,
            prev_hash=prev_hash,
            timestamp=timestamp,
            payload=payload,
            hash=entry_hash,
            chain_hash=chain_hash,
            signature_hex=sig.hex(),
        )
        with self.path.open("a") as f:
            f.write(entry.to_json() + "\n")
        return entry

    def verify_chain(self) -> bool:
        """Verify hash chain and all Ed25519 signatures.

        Returns False on any mismatch.
        """
        assert self.keypair is not None
        public_key = self.keypair.public_key

        prev_hash = "0" * 64
        prev_chain_hash = "0" * 64

        with self.path.open() as f:
            for i, line in enumerate(f):
                data = json.loads(line)
                entry = SignedOmegaEntry(**data)

                if entry.index != i:
                    return False
                if entry.prev_hash != prev_hash:
                    return False

                recomputed_hash = self._compute_entry_hash(
                    entry.index,
                    entry.prev_hash,
                    entry.timestamp,
                    entry.payload,
                )
                if entry.hash != recomputed_hash:
                    return False

                recomputed_chain = self._compute_chain_hash(prev_chain_hash, entry.hash)
                if entry.chain_hash != recomputed_chain:
                    return False

                sig_bytes = bytes.fromhex(entry.signature_hex)
                if not verify_signature(public_key, entry.chain_hash.encode(), sig_bytes):
                    return False

                prev_hash = entry.hash
                prev_chain_hash = entry.chain_hash

        return True
