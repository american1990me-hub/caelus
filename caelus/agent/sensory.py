from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict

from ..language.noetica_interpreter import interpret, ParsedUtterance
from ..graphs.semantic import SemanticGraphEngine
from ..graphs.argument import ArgumentGraphEngine


@dataclass
class ParsedSensory:
    raw_text: str
    utterance: ParsedUtterance
    semantic_snapshot: dict
    argument_snapshot: dict

    def to_dict(self) -> dict:
        return {
            "raw_text": self.raw_text,
            "utterance": self.utterance.to_dict(),
            "semantic": self.semantic_snapshot,
            "argument": self.argument_snapshot,
        }


# Singleton-ish engines for now; can be hoisted to higher-level state later.
_semantic_engine = SemanticGraphEngine()
_argument_engine = ArgumentGraphEngine()


def reset_sensory_engines() -> None:
    """Reset the stateful engines used for sensory parsing."""
    global _semantic_engine, _argument_engine
    _semantic_engine = SemanticGraphEngine()
    _argument_engine = ArgumentGraphEngine()


def parse_sensory_input(sensory_raw: Dict[str, Any]) -> ParsedSensory:
    """Parse raw sensory dict into structured ParsedSensory.

    Expected sensory_raw format:
        {"text": "user utterance"}
    """
    text = str(sensory_raw.get("text", ""))

    utterance = interpret(text)

    # Update semantic graph / argument graph
    _semantic_engine.apply_intent(utterance.intent)
    _argument_engine.add_intent_as_claim(utterance.intent, raw_text=text)

    sem_snapshot = _semantic_engine.snapshot()
    arg_snapshot = _argument_engine.snapshot()
    # Optionally mark the last claim in the snapshot; v1 we just leave as-is.

    return ParsedSensory(
        raw_text=text,
        utterance=utterance,
        semantic_snapshot=sem_snapshot,
        argument_snapshot=arg_snapshot,
    )


def get_semantic_engine() -> SemanticGraphEngine:
    return _semantic_engine


def get_argument_engine() -> ArgumentGraphEngine:
    return _argument_engine
