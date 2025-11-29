from __future__ import annotations

import tarfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class ForensicsBundleConfig:
    output_path: Path
    include_paths: list[Path]


class ForensicsBundler:
    def __init__(self, config: ForensicsBundleConfig) -> None:
        self.config = config

    def create_bundle(self) -> Path:
        """Create a tar.gz bundle with the specified files.

        Intended to include:
        - Signed Ω-ledger file
        - Any tombstone logs
        - Optional config snapshots
        """
        out_path = self.config.output_path
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with tarfile.open(out_path, "w:gz") as tar:
            for p in self.config.include_paths:
                if p.exists():
                    tar.add(str(p), arcname=p.name)

        return out_path
