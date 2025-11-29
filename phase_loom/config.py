from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PhaseLoomConfig:
    omega_dir: Path


def load_config() -> PhaseLoomConfig:
    # v1: simple env-var or default path
    import os
    base = os.environ.get("PHASELOOM_OMEGA_DIR", "./omega_logs")
    return PhaseLoomConfig(omega_dir=Path(base).expanduser().resolve())
