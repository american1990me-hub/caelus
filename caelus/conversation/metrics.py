from dataclasses import dataclass
from typing import Dict, Any, Tuple, Optional

from caelus.language_engine.trainer import CaelusLanguageTrainer, PuzzleResult
from caelus.language_engine.store import CaelusLanguageMemoryStore

GAMMA_ALPHA = 0.99  # ensures |Γ_t - Γ_{t-1}| ≤ 0.01 for a single bad step


@dataclass
class MemorySnapshot:
    vocab_difficulty: Dict[str, float]
    vocab_box: Dict[str, int]


def snapshot_memory(memory: "CaelusLanguageMemoryStore") -> MemorySnapshot:
    return MemorySnapshot(
        vocab_difficulty={w: e.difficulty for w, e in memory.vocab.items()},
        vocab_box={w: e.box for w, e in memory.vocab.items()},
    )


def memory_distance(prev: MemorySnapshot, curr: MemorySnapshot) -> float:
    """ΔM in [0, 1], scaled so that a single normal learning update is ~0.02–0.03.

    Uses |Δdifficulty| + |Δbox|/4 per word, then normalizes.
    """
    words = set(prev.vocab_difficulty.keys()) | set(curr.vocab_difficulty.keys())
    if not words:
        return 0.0

    total = 0.0
    for w in words:
        d_prev = prev.vocab_difficulty.get(w, 0.5)
        d_curr = curr.vocab_difficulty.get(w, 0.5)
        b_prev = prev.vocab_box.get(w, 1)
        b_curr = curr.vocab_box.get(w, 1)
        total += abs(d_prev - d_curr) + abs(b_prev - b_curr) / 4.0

    # Only a few words change per step. Normalize with a lower bound of 6 words
    # so ΔM for a single-word update stays small (≈0.02–0.03).
    N = max(len(words), 6)
    norm = 2.0 * N  # arbitrary but fixed scaling
    return min(1.0, total / norm)


@dataclass
class TurnMetrics:
    turn_index: int
    Gamma: float
    C_self: float
    DeltaM_repair: float
    meta: Dict[str, Any]


class CaelusConversationSimulator:
    """Wraps CaelusLanguageTrainer and exposes per-turn Gate-5 metrics:
      - Gamma      (Γ): running coherence-of-performance score
      - C_self     : 1 − ΔM (self-consistency)
      - DeltaM     : normalized change in memory state

    This is Caelus-as-student in a controlled scenario.
    """

    def __init__(self, trainer: "CaelusLanguageTrainer"):
        self.trainer = trainer
        self.memory = trainer.memory
        self.gamma: float = 1.0
        self.last_snapshot: MemorySnapshot = snapshot_memory(self.memory)
        self.turn_index: int = 0

    # ---- core metric update ----
    def _update_metrics(
        self,
        result: Optional[PuzzleResult],
        meta: Dict[str, Any],
    ) -> TurnMetrics:
        prev_snap = self.last_snapshot
        curr_snap = snapshot_memory(self.memory)
        delta_m = memory_distance(prev_snap, curr_snap)
        c_self = 1.0 - delta_m

        if result is not None:
            instant = 1.0 if result.correct else 0.0
        else:
            # non-puzzle action (e.g. introduce_vocab)
            instant = 1.0

        # Exponential filter: Γ_t = αΓ_{t−1} + (1 − α) * instant
        self.gamma = GAMMA_ALPHA * self.gamma + (1.0 - GAMMA_ALPHA) * instant

        self.turn_index += 1
        tm = TurnMetrics(
            turn_index=self.turn_index,
            Gamma=self.gamma,
            C_self=c_self,
            DeltaM_repair=delta_m,
            meta=meta,
        )
        self.last_snapshot = curr_snap
        return tm

    # ---- scenario actions ----
    def act_introduce_vocab(
        self,
        word: str,
        language: str,
        definition: str,
        example: str,
        concept_id: Optional[str] = None,
    ) -> TurnMetrics:
        self.trainer.introduce_vocab(word, language, definition, example, concept_id)
        return self._update_metrics(result=None, meta={
            "kind": "introduce_vocab",
            "word": word,
        })

    def act_vocab_mcq(self, word: str) -> Tuple[PuzzleResult, TurnMetrics]:
        result = self.trainer.train_vocab_round(word)
        tm = self._update_metrics(result=result, meta={
            "kind": "vocab_def_mcq",
            "word": word,
        })
        return result, tm

    def act_vocab_cloze(self, word: str) -> Tuple[PuzzleResult, TurnMetrics]:
        result = self.trainer.train_vocab_cloze_round(word)
        tm = self._update_metrics(result=result, meta={
            "kind": "vocab_cloze",
            "word": word,
        })
        return result, tm

    def act_grammar_order(
        self,
        sentence: str,
        language: str,
    ) -> Tuple[PuzzleResult, TurnMetrics]:
        result = self.trainer.train_grammar_round(sentence, language)
        tm = self._update_metrics(result=result, meta={
            "kind": "grammar_order",
            "sentence": sentence,
        })
        return result, tm
