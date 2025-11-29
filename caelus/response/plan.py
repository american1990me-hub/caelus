from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from typing import List, Dict

from ..language.intents import Intent
from ..graphs.semantic import SemanticGraphEngine
from ..graphs.argument import ArgumentGraphEngine
from ..context.dialogue import DialogueContext


class ResponseMode(Enum):
    DEFINITION = auto()
    EXPLANATION = auto()
    WHY = auto()
    COMPARISON = auto()
    MODIFIER_ONLY = auto()  # RIGOR / CREATIVE stand-alone
    GENERIC = auto()


@dataclass
class ResponsePlan:
    mode: ResponseMode
    focus_concepts: List[str] = field(default_factory=list)
    secondary_concepts: List[str] = field(default_factory=list)
    # Style knobs derived from intents (0 = off, 1 = on for v1)
    rigor_level: int = 0
    creative_level: int = 0
    # Optional claim id from argument graph (for traceability)
    source_claim_id: str | None = None
    # Any additional notes
    notes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.name,
            "focus_concepts": self.focus_concepts,
            "secondary_concepts": self.secondary_concepts,
            "rigor_level": self.rigor_level,
            "creative_level": self.creative_level,
            "source_claim_id": self.source_claim_id,
            "notes": dict(self.notes),
        }

def apply_context_to_plan(plan: ResponsePlan, ctx: DialogueContext) -> ResponsePlan:
    """Return a new plan with context biases applied.

    - Add ctx.rigor_bias and ctx.creative_bias to local levels (clamped).
    - If plan has no focus_concepts but context remembers last_concepts, reuse them.
    """
    # Copy to avoid mutating caller's instance
    new = ResponsePlan(
        mode=plan.mode,
        focus_concepts=list(plan.focus_concepts),
        secondary_concepts=list(plan.secondary_concepts),
        rigor_level=plan.rigor_level,
        creative_level=plan.creative_level,
        source_claim_id=plan.source_claim_id,
        notes=dict(plan.notes),
    )

    # Merge style
    new.rigor_level = max(0, min(3, new.rigor_level + ctx.rigor_bias))
    new.creative_level = max(0, min(3, new.creative_level + ctx.creative_bias))

    # If no focus concepts but we have context
    if not new.focus_concepts and ctx.last_concepts:
        new.focus_concepts = list(ctx.last_concepts)
        new.notes["focus_from_context"] = "true"

    return new


def _base_mode_for_intent(intent: Intent) -> ResponseMode:
    t = intent.type.name
    if t == "DEFINE":
        return ResponseMode.DEFINITION
    if t == "EXPLAIN":
        return ResponseMode.EXPLANATION
    if t == "WHY":
        return ResponseMode.WHY
    if t == "COMPARE":
        return ResponseMode.COMPARISON
    if t in {"RIGOR", "CREATIVE"}:
        return ResponseMode.MODIFIER_ONLY
    return ResponseMode.GENERIC


def _style_from_intent(intent: Intent) -> tuple[int, int]:
    """Return (rigor_level, creative_level) derived from this intent.

    v1: treat RIGOR/CREATIVE intents as local hints.
    """
    rigor = 0
    creative = 0
    t = intent.type.name
    if t == "RIGOR":
        rigor = 1
    if t == "CREATIVE":
        creative = 1
    return rigor, creative


def make_response_plan(
    intent: Intent,
    semantic_engine: SemanticGraphEngine,
    argument_engine: ArgumentGraphEngine,
    last_claim_id: str | None = None,
) -> ResponsePlan:
    """Construct a ResponsePlan from an Intent and the current meaning graphs.

    This is deterministic and does not mutate the graphs.
    """
    mode = _base_mode_for_intent(intent)
    rigor, creative = _style_from_intent(intent)

    focus_concepts: List[str] = list(intent.concepts)
    secondary_concepts: List[str] = list(intent.secondary_concepts)

    # If no concepts were recognized, but the semantic graph has active nodes,
    # fall back to those as focus.
    if not focus_concepts:
        active = list(semantic_engine.graph.active_nodes)
        if active:
            focus_concepts = active

    # For comparison mode, ensure we have at least two concepts if possible.
    if mode == ResponseMode.COMPARISON and len(focus_concepts) < 2:
        # Combine primary + secondary
        combined = list(intent.concepts) + list(intent.secondary_concepts)
        if len(combined) >= 2:
            focus_concepts = combined[:2]
        # If still not, fall back to active nodes
        if len(focus_concepts) < 2:
            active = list(semantic_engine.graph.active_nodes)
            if len(active) >= 2:
                focus_concepts = active[:2]

    plan = ResponsePlan(
        mode=mode,
        focus_concepts=focus_concepts,
        secondary_concepts=secondary_concepts,
        rigor_level=rigor,
        creative_level=creative,
        source_claim_id=last_claim_id,
        notes={},
    )

    # Attach simple notes for traceability
    if focus_concepts:
        plan.notes["focus_summary"] = ",".join(focus_concepts)
    if secondary_concepts:
        plan.notes["secondary_summary"] = ",".join(secondary_concepts)

    return plan
