from __future__ import annotations

from typing import Any, Dict

from ..language.intents import IntentType
from .plan import ResponsePlan, ResponseMode
from ..language.response_templates import render_template


def render_response(plan: ResponsePlan) -> str:
    """Render a response plan to a string of text, using templates."""
    mode = plan.mode
    args: Dict[str, Any] = {
        # TODO: for now we pass all concepts and let the template handle it
        # A better way would be to align with template variables.
        "concept": plan.focus_concepts[0] if plan.focus_concepts else None,
        "concept1": plan.focus_concepts[0] if plan.focus_concepts else None,
        "concept2": plan.focus_concepts[1]
        if len(plan.focus_concepts) > 1
        else plan.secondary_concepts[0]
        if plan.secondary_concepts
        else None,
    }

    # Default to generic if a suitable template is not found
    template_id = "unknown_intent"

    if mode == ResponseMode.DEFINITION:
        if plan.focus_concepts:
            if plan.rigor_level > 0:
                template_id = "define_concept_rigorous"
            else:
                template_id = "define_concept"
        else:
            template_id = "define_need_concept"

    elif mode == ResponseMode.EXPLANATION:
        template_id = (
            "explain_concept" if plan.focus_concepts else "explain_need_concept"
        )
    elif mode == ResponseMode.WHY:
        template_id = "why_concept" if plan.focus_concepts else "why_need_concept"
    elif mode == ResponseMode.COMPARISON:
        # Ensure there are two concepts for a good comparison
        can_compare = (len(plan.focus_concepts) + len(plan.secondary_concepts)) >= 2
        template_id = "compare_concepts" if can_compare else "compare_need_two"
    elif mode == ResponseMode.MODIFIER_ONLY:
        if plan.rigor_level > 0:
            template_id = "rigor_acknowledged"
        elif plan.creative_level > 0:
            template_id = "creative_acknowledged"
    elif mode == ResponseMode.GENERIC:
        template_id = "unknown_intent"  # Fallback for now

    return render_template(template_id, args=args)
