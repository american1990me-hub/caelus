
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List, Dict, Any

from ..language.intents import Intent


@dataclass
class DialogueContext:
    # Style preferences accumulated over time (clamped in [0, 3])
    rigor_bias: int = 0
    creative_bias: int = 0

    # Last focused concepts & mode (for pronouns/"it")
    last_concepts: List[str] = field(default_factory=list)
    last_mode: str | None = None  # e.g. "DEFINITION", "EXPLANATION", etc.

    # Lightweight history for debugging or later features
    history: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def wants_more_rigor(self) -> bool:
        return self.rigor_bias > 0

    # ---- State update rules ----

    def apply_intent(self, intent: Intent) -> None:
        """Update context based on the new intent.

        Rules:
        - RIGOR intents increase rigor_bias.
        - CREATIVE intents increase creative_bias.
        - Other intents may reset biases slightly towards 0 or leave them.
        - Any intent with non-empty concepts updates last_concepts + last_mode.
        """
        t = intent.type.name

        if t == "RIGOR":
            self.rigor_bias = min(self.rigor_bias + 1, 3)
        elif t == "CREATIVE":
            self.creative_bias = min(self.creative_bias + 1, 3)
        else:
            # Gentle decay towards 0 so preferences fade if not reinforced
            if self.rigor_bias > 0:
                self.rigor_bias -= 1
            if self.creative_bias > 0:
                self.creative_bias -= 1

        if intent.concepts:
            self.last_concepts = list(intent.concepts)
            self.last_mode = t

        self.history.append(
            {
                "intent_type": t,
                "concepts": list(intent.concepts),
                "secondary_concepts": list(intent.secondary_concepts),
                "rigor_bias": self.rigor_bias,
                "creative_bias": self.creative_bias,
            }
        )

    # ---- Persistence ----

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rigor_bias": self.rigor_bias,
            "creative_bias": self.creative_bias,
            "last_concepts": list(self.last_concepts),
            "last_mode": self.last_mode,
            "history": list(self.history),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DialogueContext:
        return cls(
            rigor_bias=int(data.get("rigor_bias", 0)),
            creative_bias=int(data.get("creative_bias", 0)),
            last_concepts=list(data.get("last_concepts", [])),
            last_mode=data.get("last_mode"),
            history=list(data.get("history", [])),
        )


def load_context(path: Path) -> DialogueContext:
    if not path.exists():
        return DialogueContext()
    import json
    data = path.read_text(encoding="utf-8")
    raw = json.loads(data)
    return DialogueContext.from_dict(raw)


def save_context(path: Path, ctx: DialogueContext) -> None:
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(ctx.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
