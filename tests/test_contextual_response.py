from __future__ import annotations

from pathlib import Path

from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig


def test_rigor_persists_across_sessions(tmp_path: Path) -> None:
    ledger1 = tmp_path / "omega_ctx1.log"
    ledger2 = tmp_path / "omega_ctx2.log"
    context_path = tmp_path / "ctx.json"
    policy_path = tmp_path / "policy.json"

    # Session 1: ask for more rigor
    cfg1 = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=123,
        ledger_path=ledger1,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt1 = CaelusRuntime(cfg1)
    _ = rt1.run_session("be more rigorous about coherence field")

    # Session 2: define coherence field; expect more math/rigor flavour
    cfg2 = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=123,
        ledger_path=ledger2,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt2 = CaelusRuntime(cfg2)
    reply = rt2.run_session("define coherence field")

    # Heuristic: rigorous answer should mention the formula or Γ explicitly
    lower = reply.lower()
    assert "coherence field" in lower
    assert "γ" in reply or "gamma" in reply or "=" in reply


def test_why_with_expanded_concepts(tmp_path: Path) -> None:
    ledger = tmp_path / "omega_why.log"
    context_path = tmp_path / "ctx_why.json"
    policy_path = tmp_path / "policy_why.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=42,
        ledger_path=ledger,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    reply = rt.run_session("why is the omega ledger important?")

    lower = reply.lower()
    assert "omega" in lower
    assert "ledger" in lower
    assert "matters" in lower or "important" in lower


def test_compare_new_concepts(tmp_path: Path) -> None:
    ledger = tmp_path / "omega_cmp2.log"
    context_path = tmp_path / "ctx_cmp2.json"
    policy_path = tmp_path / "policy_cmp2.json"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=7,
        ledger_path=ledger,
        context_path=context_path,
        policy_path=policy_path,
    )
    rt = CaelusRuntime(cfg)

    reply = rt.run_session("compare UFE and CACE")
    lower = reply.lower()
    assert "ufe" in lower
    assert "cace" in lower
    assert "similar" in lower or "both" in lower
    assert "differ" in lower or "difference" in lower
