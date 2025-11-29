from caelus.conversation.testing import run_scenario_with_metrics

SCENARIOS = [
    "tests/fixtures/conv_scenarios/basic_small_talk.json",
    "tests/fixtures/conv_scenarios/noetica_mix.json",
]

MAX_GAMMA_DROP = 0.01
MIN_CSELF = 0.95
MAX_DELTA_M = 0.05


def test_conversation_metrics_stable() -> None:
    for path in SCENARIOS:
        metrics = run_scenario_with_metrics(path)
        prev_gamma = None

        for m in metrics:
            gamma = m["Gamma"]
            c_self = m["C_self"]
            delta_m = m["DeltaM_repair"]

            if prev_gamma is not None:
                # Gate: turn-to-turn Γ drop ≤ 0.01
                assert (prev_gamma - gamma) <= MAX_GAMMA_DROP + 1e-9

            # Gate: C_self ≥ 0.95
            assert c_self >= MIN_CSELF

            # Gate: repair ΔM ≤ 0.05
            assert delta_m <= MAX_DELTA_M

            prev_gamma = gamma
