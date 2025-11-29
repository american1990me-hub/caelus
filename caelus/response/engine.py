from __future__ import annotations

from typing import Any, Dict

from ..agent.sensory import ParsedSensory, get_semantic_engine, get_argument_engine
from ..context.dialogue import DialogueContext
from .plan import make_response_plan, apply_context_to_plan
from .render import render_response


def build_response_from_sensory_with_context(
    sensory: ParsedSensory, ctx: DialogueContext
) -> Dict[str, Any]:
    """Given a ParsedSensory snapshot and dialogue context, build a reply and plan."""
    sem_engine = get_semantic_engine()
    arg_engine = get_argument_engine()

    base_plan = make_response_plan(
        intent=sensory.utterance.intent,
        semantic_engine=sem_engine,
        argument_engine=arg_engine,
        last_claim_id=None,
    )

    plan = apply_context_to_plan(base_plan, ctx)
    reply_text = render_response(plan)

    return {
        "reply_text": reply_text,
        "plan": plan.to_dict(),
        "sensory": sensory.to_dict(),
    }
