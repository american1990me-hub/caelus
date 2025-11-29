from __future__ import annotations

import random
from typing import Dict, Any


# --- Concept name helpers ---
# (can be expanded with grammar rules, etc.)

_CONCEPT_FRIENDLY_NAMES: Dict[str, str] = {
    "sem:coherence_field": "the coherence field",
    "sem:caelus": "Caelus",
    "sem:noetica": "Noetica",
    "sem:omega_tethernet": "the Omega-Tethernet",
    "sem:cace": "CACE",
    "sem:ufe": "the Universal Field Equation (UFE)",
    "sem:omega_ledger": "the Omega Ledger",
}


def _get_concept_name(cid: str) -> str:
    return _CONCEPT_FRIENDLY_NAMES.get(cid, cid)


# --- Template definitions ---

_TEMPLATES: Dict[str, list[str]] = {
    "unknown_intent": [
        "I'm not sure what you mean.",
        "Could you rephrase that?",
        "I don't understand.",
    ],
    "internal_error": [
        "I've run into an internal error. Please try again.",
    ],
    "compare_need_two": [
        "Comparison needs at least two concrete concepts. I only see one right now.",
    ],
    "compare_concepts": [
        "The main difference between {concept1} and {concept2} is...",
        "Both {concept1} and {concept2} are key concepts, but they operate at different levels.",
        "Let's compare {concept1} and {concept2}.",
    ],
    "why_need_concept": [
        "I can answer 'why' more concretely once I know which concept you mean.",
    ],
    "why_concept": [
        "The {concept} matters because it turns Caelus from a black box into an auditable instrument.",
        "The core idea of {concept} is to enable...",
        "{concept} is important for the stability of the system.",
    ],
    "define_need_concept": [
        "What concept do you want me to define?",
    ],
    "define_concept": [
        "{concept} is a core component of the Caelus system.",
        "In short, {concept} is...",
    ],
    "define_concept_rigorous": [
        "Rigorously, {concept} is defined by the equation Γ = f(ψ).",
    ],
    "explain_need_concept": [
        "What concept do you want me to explain?",
    ],
    "explain_concept": [
        "Let me explain {concept}.",
        "Here is a brief explanation of {concept}:",
    ],
    "rigor_acknowledged": [
        "Understood. I will be more rigorous.",
        "Switching to a more rigorous mode.",
    ],
    "creative_acknowledged": [
        "Okay, let's get creative!",
        "Engaging creative mode.",
    ],
}

def render_template(template_id: str, args: Dict[str, Any] | None = None) -> str:
    """Render a template by ID, filling in arguments.

    Selects a template from the list at random.
    """
    if args is None:
        args = {}

    # Pre-process args to make them friendly
    processed_args: Dict[str, Any] = {}
    for k, v in args.items():
        if isinstance(v, str) and v.startswith("sem:"):
            processed_args[k] = _get_concept_name(v)
        else:
            processed_args[k] = v

    template_choices = _TEMPLATES.get(template_id)
    if not template_choices:
        return f"Error: template '{template_id}' not found."

    # Seed random for determinism if a seed is present in args
    seed = processed_args.get("seed")
    if seed is not None:
        random.seed(seed)

    chosen_template = random.choice(template_choices)
    return chosen_template.format(**processed_args)
