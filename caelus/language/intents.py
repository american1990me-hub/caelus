from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class IntentType(Enum):
    DEFINE = auto()
    EXPLAIN = auto()
    WHY = auto()
    COMPARE = auto()
    RIGOR = auto()
    CREATIVE = auto()
    UNKNOWN = auto()


@dataclass
class Intent:
    type: IntentType
    # canonical concept ids, e.g. ["sem:coherence", "sem:field"]
    concepts: List[str]
    # free-form target text spans (for debugging / display)
    targets: List[str]
    # secondary concept(s) e.g. for COMPARE
    secondary_concepts: List[str]
    secondary_targets: List[str]

    def to_dict(self) -> dict:
        return {
            "type": self.type.name,
            "concepts": self.concepts,
            "targets": self.targets,
            "secondary_concepts": self.secondary_concepts,
            "secondary_targets": self.secondary_targets,
        }
