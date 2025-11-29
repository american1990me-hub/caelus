from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import paths
from .math_core.coherence import CoherenceContract


@dataclass
class CaelusConfig:
    """Caelus configuration settings."""

    run_name: str = "default-run"
    log_dir: Path = paths.LOG_DIR
    n: int = 128
    dt: float = 0.01
    autocurl_u: bool = True
    autocurl_v: bool = False
    h_u: float = 0.0
    h_v: float = 0.0

COHERENCE = CoherenceContract()
PATHS = paths
