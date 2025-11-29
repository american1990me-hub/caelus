from __future__ import annotations

from typing import Dict, Tuple

from .plan import ResponsePlan, ResponseMode


# Minimal concept fact base for v1.
CONCEPT_FACTS: Dict[str, Dict[str, str]] = {
    "sem:coherence_field": {
        "label": "coherence field",
        "short": (
            "a scalar observable Γ(t) that measures how aligned the vorticity "
            "field is with the velocity field across space."
        ),
        "math": (
            "Γ(t) = 1 − ∫‖∇×u − λu‖² dx / ∫‖∇u‖² dx, "
            "with λ = ⟨∇×u, u⟩ / ⟨u, u⟩."
        ),
        "caelus_role": (
            "It tells Caelus whether the underlying dynamics are structured "
            "(Γ ≈ 1, Beltrami-like) or feral/chaotic (Γ significantly < 1)."
        ),
        "analogy": (
            "You can think of it as a 'order meter' for flows: the closer to 1, "
            "the more the motion lines up into a coherent pattern."
        ),
    },
    "sem:caelus": {
        "label": "Caelus",
        "short": (
            "a coherence-first Noetican cognition engine that runs on GM-OS."
        ),
        "math": (
            "Internally it evolves a complex field ψ on a manifold and tracks "
            "coherence via functionals like C[ψ] and Γ(t)."
        ),
        "caelus_role": (
            "Caelus is the agent that perceives, reasons, and speaks using "
            "the coherence metrics as internal state."
        ),
        "analogy": (
            "You can think of Caelus as a scientist-operator living inside a "
            "field simulator, constantly checking how ordered the universe is."
        ),
    },
    "sem:noetica": {
        "label": "Noetica",
        "short": (
            "a designed language for meaning-first interaction with Caelus."
        ),
        "math": (
            "It maps surface forms (glyphs, proto-Latin, English) into "
            "structured semantic fields that can couple to ψ and Γ."
        ),
        "caelus_role": (
            "Noetica is the interface layer that turns human requests into "
            "structured operations on Caelus' internal graphs and fields."
        ),
        "analogy": (
            "You can think of Noetica as the 'control panel language' that "
            "Caelus speaks natively."
        ),
    },
    "sem:omega_tethernet": {
        "label": "Ω-TetherNet",
        "short": (
            "a social/sensorial field wiring multiple agents and their Ω-ledgers "
            "into a shared coherence space."
        ),
        "math": (
            "It can be modelled as a multi-agent graph where each node is a "
            "Caelus-like process with its own ψ, Γ, and Ω-chain."
        ),
        "caelus_role": (
            "It lets Caelus sense and respond to other agents as structured "
            "coherence fields, not just text streams."
        ),
        "analogy": (
            "Imagine a nervous system that connects many Caelus instances into "
            "one large perceiving web."
        ),
    },
    "sem:cace": {
        "label": "CACE",
        "short": (
            "the Coherence-Aware Compute Engine that runs tensor operations "
            "and logs their coherence behaviour."
        ),
        "math": (
            "It wraps matmuls and layers with coherence metrics and produces "
            "Ω-style receipts per layer."
        ),
        "caelus_role": (
            "CACE is how Caelus actually runs neural models while monitoring "
            "their internal coherence."
        ),
        "analogy": (
            "Think of it as a GPU that constantly reports how 'well-behaved' "
            "each computation is."
        ),
    },
}

CONCEPT_FACTS.update(
    {
        "sem:ufe": {
            "label": "UFE",
            "short": (
                "the underlying field evolution engine that updates ψ over time "
                "subject to a coherence contract."
            ),
            "math": (
                "It integrates ψ_t = L[ψ] + N[ψ] − κ δC/δψ* with adaptive time "
                "stepping so C[ψ] does not grow too fast."
            ),
            "caelus_role": (
                "UFE is the dynamical backbone of Caelus: it defines how the "
                "internal world-state evolves."
            ),
            "analogy": (
                "Think of UFE as the physics engine inside Caelus' universe."
            ),
        },
        "sem:omega_ledger": {
            "label": "Ω-ledger",
            "short": (
                "a signed, hash-chained log of every significant event inside "
                "Caelus."
            ),
            "math": (
                "Each entry stores index, prev_hash, payload, and hash, and is "
                "signed with an Ed25519 key."
            ),
            "caelus_role": (
                "It turns Caelus from a black box into an auditable instrument."
            ),
            "analogy": (
                "You can think of the Ω-ledger as Caelus' lab notebook that "
                "cannot be silently edited."
            ),
        },
    }
)

# Comparison facts keyed by ordered pairs of concept ids.
COMPARISON_FACTS: Dict[Tuple[str, str], Dict[str, str]] = {
    ("sem:caelus", "sem:noetica"): {
        "similar": (
            "Both Caelus and Noetica are parts of the same stack: they are "
            "designed to work together as a meaning-first system."
        ),
        "different": (
            "Caelus is the agent doing the reasoning and coherence tracking, "
            "while Noetica is the language/interface used to talk to that agent."
        ),
    },
    ("sem:coherence_field", "sem:cace"): {
        "similar": (
            "Both the coherence field Γ and CACE care about structure in "
            "computations: they distinguish ordered from noisy behaviour."
        ),
        "different": (
            "Γ is a physical/field-level observable on flows, whereas CACE is "
            "a compute engine that applies coherence ideas to tensor ops."
        ),
    },
}

COMPARISON_FACTS.update(
    {
        ("sem:ufe", "sem:cace"): {
            "similar": (
                "Both UFE and CACE are engines that run computations under "
                "coherence-related constraints."
            ),
            "different": (
                "UFE operates on physical/field state ψ, whereas CACE operates "
                "on neural tensors and layer activations."
            ),
        },
        ("sem:omega_ledger", "sem:omega_tethernet"): {
            "similar": (
                "Both structures use Ω as a prefix because they organize how "
                "agents and their histories are coordinated."
            ),
            "different": (
                "Ω-ledger is per-agent history, while Ω-TetherNet is the graph "
                "that connects many such histories into a social field."
            ),
        },
    }
)

def _concept_label(cid: str) -> str:
    info = CONCEPT_FACTS.get(cid)
    if info is not None:
        return info.get("label", cid)
    return cid


def _get_concept_info(cid: str) -> Dict[str, str]:
    return CONCEPT_FACTS.get(
        cid,
        {
            "label": cid,
            "short": f"{cid} is a concept inside Caelus.",
            "math": "",
            "caelus_role": "",
            "analogy": "",
        },
    )

def _render_definition(plan: ResponsePlan) -> str:
    if not plan.focus_concepts:
        return "I do not see a specific concept to define yet."

    cid = plan.focus_concepts[0]
    info = _get_concept_info(cid)

    parts: list[str] = []
    parts.append(
        f"In Caelus, {_concept_label(cid)} is {info['short']}"
    )

    if plan.rigor_level and info.get("math"):
        parts.append("Mathematically, " + info["math"])

    if info.get("caelus_role"):
        parts.append(info["caelus_role"])

    if plan.creative_level and info.get("analogy"):
        parts.append("Intuitively, " + info["analogy"])

    return " ".join(p.strip() for p in parts if p.strip())


def _render_explanation(plan: ResponsePlan) -> str:
    # v1: explanation is a slightly expanded definition.
    text = _render_definition(plan)
    if plan.rigor_level:
        text += " This explanation is tuned to be more rigorous and math-heavy."
    if plan.creative_level:
        text += " I'm also leaning a bit more into analogy and intuition."
    return text


def _render_why(plan: ResponsePlan) -> str:
    if not plan.focus_concepts:
        return "I can answer 'why' more concretely once I know which concept you mean."

    cid = plan.focus_concepts[0]
    info = _get_concept_info(cid)

    base = info.get("caelus_role") or info.get("short") or "it matters inside Caelus."
    text = f"It matters because {base}"

    if plan.rigor_level and info.get("math"):
        text += " From a coherence perspective, " + info["math"]

    return text


def _render_comparison(plan: ResponsePlan) -> str:
    if len(plan.focus_concepts) < 2:
        return "Comparison needs at least two concrete concepts." \
               " I only see one right now."

    a, b = plan.focus_concepts[0], plan.focus_concepts[1]
    info_a = _get_concept_info(a)
    info_b = _get_concept_info(b)

    pair = (a, b)
    if pair not in COMPARISON_FACTS and (b, a) in COMPARISON_FACTS:
        pair = (b, a)
    facts = COMPARISON_FACTS.get(pair)

    label_a = _concept_label(a)
    label_b = _concept_label(b)

    parts: list[str] = []

    parts.append(f"{label_a} is {info_a['short']}")
    parts.append(f"{label_b} is {info_b['short']}")

    if facts is not None:
        parts.append("They are similar because " + facts["similar"])
        parts.append("They differ because " + facts["different"])
    else:
        parts.append(
            "They are related concepts inside the Caelus/Noetica stack, but I "
            "don't yet have a hand-written similarity/difference summary."
        )

    if plan.rigor_level:
        parts.append(
            "This summary is slightly more technical because you asked for "
            "more rigor."
        )
    if plan.creative_level:
        parts.append(
            "I'm also leaning a bit more into analogy and big-picture language "
            "because of the creative modifier."
        )

    return " ".join(p.strip() for p in parts if p.strip())


def _render_modifier_only(plan: ResponsePlan) -> str:
    if plan.rigor_level and not plan.creative_level:
        return (
            "Got it: you want more rigor. I'll emphasize math, explicit "
            "assumptions, and clear contracts in my next answers."
        )
    if plan.creative_level and not plan.rigor_level:
        return (
            "Understood: you want more creativity. I'll use more analogies "
            "and high-level patterns while staying grounded."
        )
    if plan.creative_level and plan.rigor_level:
        return (
            "You want both rigor and creativity: I'll try to balance precise "
            "math with intuitive metaphors."
        )
    return "I registered your preference, but I don't see a concrete concept yet."


def _render_generic(plan: ResponsePlan) -> str:
    return (
        "I parsed your request but did not map it to a specific definition, "
        "explanation, comparison, or modifier. You can say things like 'define "
        "coherence field' or 'compare Caelus and Noetica'."
    )


def render_response(plan: ResponsePlan) -> str:
    """Render a textual reply from a ResponsePlan.

    Pure function: it does not mutate any external state.
    """
    mode = plan.mode
    if mode == ResponseMode.DEFINITION:
        return _render_definition(plan)
    if mode == ResponseMode.EXPLANATION:
        return _render_explanation(plan)
    if mode == ResponseMode.WHY:
        return _render_why(plan)
    if mode == ResponseMode.COMPARISON:
        return _render_comparison(plan)
    if mode == ResponseMode.MODIFIER_ONLY:
        return _render_modifier_only(plan)
    return _render_generic(plan)
