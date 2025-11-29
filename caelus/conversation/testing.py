import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from caelus.language_engine.store import CaelusLanguageMemoryStore
from caelus.language_engine.trainer import CaelusLanguageTrainer

from caelus.conversation.metrics import (
    CaelusConversationSimulator,
    TurnMetrics,
)
from caelus.ledger.signed_ledger import SignedOmegaLedger
from caelus.conversation.omega_bridge import (
    append_turn_metrics_to_ledger,
    append_conversation_summary,
)

def run_scenario_with_metrics(
    path: str,
    ledger: Optional[SignedOmegaLedger] = None,
    session_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Run a scripted Caelus-as-student scenario and return per-turn metrics.

    If `ledger` is provided, append Gate-5 metrics into Ω as conversation events.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    scenario_name = data.get("name", Path(path).stem)

    memory = CaelusLanguageMemoryStore()
    trainer = CaelusLanguageTrainer(memory)
    sim = CaelusConversationSimulator(trainer)

    metrics_log: List[Dict[str, Any]] = []
    turn_objects: List[TurnMetrics] = []

    if session_id is None:
        session_id = f"conv_{uuid.uuid4().hex[:8]}"

    for step in data["steps"]:
        action = step["action"]

        if action == "introduce_vocab":
            tm: TurnMetrics = sim.act_introduce_vocab(
                word=step["word"],
                language=step["language"],
                definition=step["definition"],
                example=step["example"],
                concept_id=step.get("concept_id"),
            )
            turn_objects.append(tm)
            metrics_log.append({
                "Gamma": tm.Gamma,
                "C_self": tm.C_self,
                "DeltaM_repair": tm.DeltaM_repair,
                "meta": tm.meta,
            })

        elif action == "puzzle_vocab_mcq":
            result, tm = sim.act_vocab_mcq(step["word"])
            turn_objects.append(tm)
            metrics_log.append({
                "Gamma": tm.Gamma,
                "C_self": tm.C_self,
                "DeltaM_repair": tm.DeltaM_repair,
                "meta": {**tm.meta, "correct": result.correct},
            })

        elif action == "puzzle_vocab_cloze":
            result, tm = sim.act_vocab_cloze(step["word"])
            turn_objects.append(tm)
            metrics_log.append({
                "Gamma": tm.Gamma,
                "C_self": tm.C_self,
                "DeltaM_repair": tm.DeltaM_repair,
                "meta": {**tm.meta, "correct": result.correct},
            })

        elif action == "puzzle_grammar_order":
            result, tm = sim.act_grammar_order(
                sentence=step["sentence"],
                language=step["language"],
            )
            turn_objects.append(tm)
            metrics_log.append({
                "Gamma": tm.Gamma,
                "C_self": tm.C_self,
                "DeltaM_repair": tm.DeltaM_repair,
                "meta": {**tm.meta, "correct": result.correct},
            })

        else:
            raise ValueError(f"Unknown action: {action}")

        # Per-turn Ω logging
        if ledger is not None:
            append_turn_metrics_to_ledger(
                ledger=ledger,
                session_id=session_id,
                scenario_name=scenario_name,
                turn_metrics=turn_objects[-1],
            )

    # Conversation-level summary
    if ledger is not None and turn_objects:
        append_conversation_summary(
            ledger=ledger,
            session_id=session_id,
            scenario_name=scenario_name,
            metrics_log=turn_objects,
        )

    return metrics_log
