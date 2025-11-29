from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from .intents import IntentType, Intent
from .lexicon import canonical_concept_ids


@dataclass
class ParsedUtterance:
    raw: str
    normalized: str
    tokens: List[str]
    intent: Intent

    def to_dict(self) -> dict:
        return {
            "raw": self.raw,
            "normalized": self.normalized,
            "tokens": self.tokens,
            "intent": self.intent.to_dict(),
        }


# --- simple normalization & tokenization ---

_WHITESPACE_RE = re.compile(r"\s+")
_NONALNUM_RE = re.compile(r"[^a-zA-Z0-9]+")


def _normalize(text: str) -> str:
    text = text.strip()
    # Collapse whitespace
    text = _WHITESPACE_RE.sub(" ", text)
    return text


def _tokenize(norm: str) -> List[str]:
    # Simple split; retain case-insensitive behaviour elsewhere.
    return [t for t in norm.split(" ") if t]


# --- intent detection rules ---


def _detect_intent_type(norm_lower: str) -> IntentType:
    # Order matters: more specific first.

    # Compare patterns
    if "compare" in norm_lower or "difference between" in norm_lower:
        return IntentType.COMPARE

    # Why-causality
    if norm_lower.startswith("why ") or " why " in norm_lower:
        return IntentType.WHY

    # Define / what is
    if norm_lower.startswith("define ") or norm_lower.startswith("what is ") or norm_lower.startswith("what's "):
        return IntentType.DEFINE

    # Explain
    if norm_lower.startswith("explain ") or " explain " in norm_lower:
        return IntentType.EXPLAIN

    # Rigor / more precise
    if "more rigorous" in norm_lower or "be rigorous" in norm_lower or "more precise" in norm_lower:
        return IntentType.RIGOR

    # Creative mode hints
    if "more creative" in norm_lower or "be creative" in norm_lower or "go wild" in norm_lower:
        return IntentType.CREATIVE

    return IntentType.UNKNOWN


def _extract_compare_targets(norm: str) -> tuple[str, str]:
    """Heuristic extraction of two compare targets.

    Examples:
      "compare coherence field and cace" → ("coherence field", "cace")
    """
    # Look for "compare X and Y" or "difference between X and Y".
    lower = norm.lower()

    m = re.search(r"compare (.+?) and (.+)", lower)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    m = re.search(r"difference between (.+?) and (.+)", lower)
    if m:
        return m.group(1).strip(), m.group(2).strip()

    # Fallback: split by " vs "
    if " vs " in lower:
        left, right = lower.split(" vs ", 1)
        return left.strip(), right.strip()

    return lower, ""


def _strip_leading_phrase(norm: str, prefixes: List[str]) -> str:
    lower = norm.lower()
    for p in prefixes:
        if lower.startswith(p):
            return norm[len(p) :].strip()
    return norm


def interpret(text: str) -> ParsedUtterance:
    """Parse an English utterance into a ParsedUtterance with Intent.

    Deterministic, rule-based, no external dependencies.
    """
    norm = _normalize(text)
    norm_l = norm.lower()
    tokens = _tokenize(norm)

    intent_type = _detect_intent_type(norm_l)

    primary_targets: List[str] = []
    secondary_targets: List[str] = []

    if intent_type == IntentType.COMPARE:
        t1, t2 = _extract_compare_targets(norm)
        if t1:
            primary_targets.append(t1)
        if t2:
            secondary_targets.append(t2)
    elif intent_type in (IntentType.DEFINE, IntentType.EXPLAIN, IntentType.WHY):
        stripped = _strip_leading_phrase(
            norm,
            ["define ", "what is ", "what's ", "explain ", "why "],
        )
        if stripped:
            primary_targets.append(stripped)
    else:
        # For RIGOR/CREATIVE/UNKNOWN, we treat the whole utterance as context.
        if norm:
            primary_targets.append(norm)

    # Canonical concept IDs from primary and secondary target spans.
    primary_concepts: List[str] = []
    for t in primary_targets:
        for cid in canonical_concept_ids(t):
            if cid not in primary_concepts:
                primary_concepts.append(cid)

    secondary_concepts: List[str] = []
    for t in secondary_targets:
        for cid in canonical_concept_ids(t):
            if cid not in secondary_concepts and cid not in primary_concepts:
                secondary_concepts.append(cid)

    intent = Intent(
        type=intent_type,
        concepts=primary_concepts,
        targets=primary_targets,
        secondary_concepts=secondary_concepts,
        secondary_targets=secondary_targets,
    )

    return ParsedUtterance(raw=text, normalized=norm, tokens=tokens, intent=intent)
