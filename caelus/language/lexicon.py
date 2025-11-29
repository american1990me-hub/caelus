from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class Concept:
    id: str
    aliases: List[str]


# Minimal lexicon for v1; extend as needed.
_CONCEPTS: List[Concept] = [
    Concept(
        id="sem:coherence_field",
        aliases=[
            "coherence field",
            "coherence density",
            "coherence",
            "gamma",
        ],
    ),
    Concept(
        id="sem:caelus",
        aliases=[
            "caelus",
            "caelus agent",
            "caelus system",
        ],
    ),
    Concept(
        id="sem:noetica",
        aliases=[
            "noetica",
            "noetican language",
            "noetican",
        ],
    ),
    Concept(
        id="sem:omega_tethernet",
        aliases=[
            "omega-tethernet",
            "ω-tethernet",
            "omega tethernet",
            "tethernet",
        ],
    ),
    Concept(
        id="sem:cace",
        aliases=[
            "cace",
            "coherence-aware compute engine",
            "coherence aware compute engine",
        ],
    ),
    Concept(
        id="sem:ufe",
        aliases=[
            "ufe",
            "universal field equation",
        ],
    ),
    Concept(
        id="sem:omega_ledger",
        aliases=[
            "omega ledger",
            "Ω-ledger",
            "omega log",
        ],
    ),
]


# Build lowercase alias → id map
_ALIAS_TO_ID: Dict[str, str] = {}
for c in _CONCEPTS:
    for a in c.aliases:
        _ALIAS_TO_ID[a.lower()] = c.id


def canonical_concept_ids(text: str) -> List[str]:
    """Return a (possibly empty) list of concept IDs that appear in `text`.

    Matching is done by simple case-insensitive substring search using aliases.
    Results are deduplicated while preserving the order in which concepts appear.
    """
    text_l = text.lower()
    found: List[str] = []

    # Iterate over concepts in _CONCEPTS order for deterministic behaviour
    for c in _CONCEPTS:
        cid = c.id
        if cid in found:
            continue
        for alias in c.aliases:
            if alias.lower() in text_l:
                found.append(cid)
                break

    return found
