from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class PhaseLoomConfig:
    omega_dir: Path


def load_config() -> PhaseLoomConfig:
    # v1: simple env-var or default path
    import os
    # The run_loop.py script saves ledger files to the `ledgers` directory.
    base = os.environ.get("PHASELOOM_OMEGA_DIR", "./ledgers")
    config = PhaseLoomConfig(omega_dir=Path(base).expanduser().resolve())
    
    # Ensure the omega_dir exists
    config.omega_dir.mkdir(parents=True, exist_ok=True)
    
    return config
