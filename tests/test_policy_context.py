from __future__ import annotations

from pathlib import Path

from caelus.context.policy import PolicyContext, save_policy_context, load_policy_context
from caelus.cace.runtime_model import ComputeCoherenceSnapshot


def test_policy_context_round_trip(tmp_path: Path) -> None:
    ctx = PolicyContext(
        eldritch_state=[2, 1, 0],
        rank_max=16,
        tau_high=0.8,
        tau_mid=0.25,
    )
    path = tmp_path / "policy.json"
    save_policy_context(path, ctx)

    ctx2 = load_policy_context(path)
    assert ctx2.eldritch_state == [2, 1, 0]
    assert ctx2.rank_max == 16
    assert ctx2.tau_high == 0.8
    assert ctx2.tau_mid == 0.25


def test_policy_context_update_from_stats() -> None:
    ctx = PolicyContext()
    snap = ComputeCoherenceSnapshot(
        mean_c_in=0.4,
        mean_c_out=0.9,
        max_abs_R_c=0.02,
        num_layers=2,
    )

    record = ctx.update_from_stats(field_gamma=0.95, snapshot=snap)

    assert "eldritch_state" in record
    assert len(record["eldritch_state"]) == 3
    assert ctx.rank_max >= 4
    assert 0.5 <= ctx.tau_high <= 0.9
    assert 0.1 <= ctx.tau_mid <= ctx.tau_high
