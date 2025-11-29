from __future__ import annotations

from caelus.policy.eldritch import bin_0_1_to_Z3, EldritchState, policy_from_eldritch_state, state_from_stats


def test_bin_0_1_to_Z3_basic() -> None:
    assert bin_0_1_to_Z3(0.0) == 0
    assert bin_0_1_to_Z3(0.1) == 0
    assert bin_0_1_to_Z3(0.4) == 1
    assert bin_0_1_to_Z3(0.8) == 2


def test_policy_from_eldritch_state_rank_and_thresholds() -> None:
    base_rank = 8
    base_th = 0.7
    base_tm = 0.3

    # a=0 → more conservative rank
    st_low = EldritchState(a=0, b=1, c=1)
    p_low = policy_from_eldritch_state(st_low, base_rank, base_th, base_tm)
    assert p_low["rank_max"] <= base_rank

    # a=2 → more expressive rank
    st_high = EldritchState(a=2, b=1, c=1)
    p_high = policy_from_eldritch_state(st_high, base_rank, base_th, base_tm)
    assert p_high["rank_max"] >= base_rank


def test_state_from_stats_ranges() -> None:
    st = state_from_stats(field_gamma=0.9, mean_c_out=0.2, concentration_proxy=0.05)
    a, b, c = st.as_tuple()
    assert a in (1, 2)  # high gamma
    assert b in (0, 1, 2)
    assert c in (0, 1, 2)
