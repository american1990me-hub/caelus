from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives import serialization


DEFAULT_KEY_DIR = Path.home() / ".caelus"
DEFAULT_PRIV_KEY_PATH = DEFAULT_KEY_DIR / "omega_ed25519_private.pem"
DEFAULT_PUB_KEY_PATH = DEFAULT_KEY_DIR / "omega_ed25519_public.pem"


@dataclass
class OmegaKeyPair:
    private_key: Ed25519PrivateKey
    public_key: Ed25519PublicKey

    def public_bytes_hex(self) -> str:
        raw = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        return raw.hex()


def _ensure_key_dir(path: Path = DEFAULT_KEY_DIR) -> None:
    path.mkdir(mode=0o700, parents=True, exist_ok=True)


def generate_keypair(
    priv_path: Path = DEFAULT_PRIV_KEY_PATH,
    pub_path: Path = DEFAULT_PUB_KEY_PATH,
) -> OmegaKeyPair:
    """Generate a new Ed25519 keypair and write it to disk.

    Private key is stored in PEM format with mode 0o600.
    Public key is stored as raw hex in a small JSON file.
    """
    _ensure_key_dir(priv_path.parent)

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    priv_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    priv_path.write_bytes(priv_bytes)
    priv_path.chmod(0o600)

    pub_raw = public_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    pub_json = {"ed25519_public_hex": pub_raw.hex()}
    pub_path.write_text(json.dumps(pub_json, indent=2))

    return OmegaKeyPair(private_key=private_key, public_key=public_key)


def load_keypair(
    priv_path: Path = DEFAULT_PRIV_KEY_PATH,
    pub_path: Path = DEFAULT_PUB_KEY_PATH,
) -> OmegaKeyPair:
    """Load an existing Ed25519 keypair from disk.

    If keys do not exist, they are generated.
    """
    if not priv_path.exists() or not pub_path.exists():
        return generate_keypair(priv_path, pub_path)

    priv_bytes = priv_path.read_bytes()
    private_key = serialization.load_pem_private_key(
        priv_bytes,
        password=None,
    )
    if not isinstance(private_key, Ed25519PrivateKey):
        raise TypeError("Expected Ed25519 private key")

    pub_json = json.loads(pub_path.read_text())
    pub_hex = pub_json["ed25519_public_hex"]
    pub_raw = bytes.fromhex(pub_hex)
    public_key = Ed25519PublicKey.from_public_bytes(pub_raw)

    return OmegaKeyPair(private_key=private_key, public_key=public_key)


def sign_bytes(keypair: OmegaKeyPair, data: bytes) -> bytes:
    return keypair.private_key.sign(data)


def verify_signature(public_key: Ed25519PublicKey, data: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, data)
        return True
    except Exception:
        return False
