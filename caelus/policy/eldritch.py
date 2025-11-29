from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class EldritchState:
    """Discrete triadic state in Z3^3 used to control CACE policy.

    Components a, b, c ∈ {0,1,2}.
    """

    a: int
    b: int
    c: int

    def as_tuple(self) -> tuple[int, int, int]:
        return (int(self.a), int(self.b), int(self.c))


def bin_0_1_to_Z3(x: float) -> int:
    """Map a real value in [0,1] into {0,1,2}.

    x < 1/3  → 0 (low)
    1/3 ≤ x < 2/3 → 1 (medium)
    x ≥ 2/3 → 2 (high)
    Values outside [0,1] are clamped.
    """
    if x <= 0.0:
        return 0
    if x >= 1.0:
        return 2
    if x < 1.0 / 3.0:
        return 0
    if x < 2.0 / 3.0:
        return 1
    return 2


def eldritch_step(state: EldritchState) -> EldritchState:
    """Simple triadic map on Z3^3.

    (a, b, c) → (b, c, (a + b + c) mod 3).

    This injects a bit of memory and coupling across components.
    """
    a, b, c = state.as_tuple()
    a_new = b % 3
    b_new = c % 3
    c_new = (a + b + c) % 3
    return EldritchState(a=a_new, b=b_new, c=c_new)


def state_from_stats(
    field_gamma: float,
    mean_c_out: float,
    concentration_proxy: float,
    concentration_scale: float = 0.1,
) -> EldritchState:
    """Construct an EldritchState from coherence observables.

    Args:
      field_gamma: Γ ∈ ℝ, typically in [0,1]. Measures field/flow coherence.
      mean_c_out: mean output coherence of CACE layers in [0,1].
      concentration_proxy: non-negative, e.g. max |R_c| across layers.
      concentration_scale: scale factor to map concentration_proxy into [0,1].
    """
    g = max(0.0, min(1.0, field_gamma))
    c_out = max(0.0, min(1.0, mean_c_out))

    # Map concentration into [0,1] via saturation
    if concentration_scale <= 0.0:
        concentration_scale = 0.1
    conc = concentration_proxy / concentration_scale
    if conc > 1.0:
        conc = 1.0
    if conc < 0.0:
        conc = 0.0

    a = bin_0_1_to_Z3(g)
    b = bin_0_1_to_Z3(c_out)
    c = bin_0_1_to_Z3(conc)
    return EldritchState(a=a, b=b, c=c)


def policy_from_eldritch_state(
    state: EldritchState,
    base_rank_max: int = 8,
    base_tau_high: float = 0.7,
    base_tau_mid: float = 0.3,
) -> Dict[str, float | int]:
    """Map EldritchState to CACE CAM policy parameters.

    Intuition:
      - a controls rank_max:
          a = 0 → more conservative low-rank (smaller rank_max)
          a = 1 → base rank_max
          a = 2 → allow higher rank_max (more expressivity)
      - b nudges tau_high (threshold for low-rank usage):
          b = 0 → slightly higher tau_high (require more coherence)
          b = 1 → base tau_high
          b = 2 → slightly lower tau_high (allow low-rank more often)
      - c nudges tau_mid (not heavily used in v1, but prepared):
          c = 0 → tau_mid closer to tau_high (narrow band)
          c = 1 → base tau_mid
          c = 2 → lower tau_mid (wider mid band)
    """
    a, b, c = state.as_tuple()

    # rank_max
    if a == 0:
        rank_max = max(4, base_rank_max // 2)
    elif a == 1:
        rank_max = base_rank_max
    else:
        rank_max = base_rank_max * 2

    # tau_high
    if b == 0:
        tau_high = min(0.9, base_tau_high + 0.1)
    elif b == 1:
        tau_high = base_tau_high
    else:  # b == 2
        tau_high = max(0.5, base_tau_high - 0.1)

    # tau_mid
    if c == 0:
        tau_mid = min(tau_high - 1e-3, base_tau_mid + 0.1)
    elif c == 1:
        tau_mid = base_tau_mid
    else:  # c == 2
        tau_mid = max(0.1, base_tau_mid - 0.1)

    return {
        "rank_max": int(rank_max),
        "tau_high": float(tau_high),
        "tau_mid": float(tau_mid),
    }
