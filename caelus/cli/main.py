from __future__ import annotations

import argparse
from pathlib import Path

from ..config import COHERENCE, PATHS, CaelusConfig
from ..ledger.omega_ledger import OmegaLedger
from ..math_core.coherence import CoherenceContract
from ..math_core.ufe import UFEStepper
from ..math_core.test_fields import make_swirl_field, make_random_field, add_galilean_boost
from ..agent.loops import CaelusInnerLoop, make_initial_state
from ..runtime.runtime import CaelusRuntime, CaelusRuntimeConfig

def cmd_run(args: argparse.Namespace) -> None:
    ledger_path = Path(args.ledger)
    ledger = OmegaLedger(ledger_path)
    contract = CoherenceContract(
        kappa=COHERENCE.kappa,
        epsilon=COHERENCE.epsilon,
    )
    stepper = UFEStepper(contract)
    inner = CaelusInnerLoop(stepper=stepper, contract=contract, ledger=ledger)

    state = make_initial_state((64, 64), contract)

    for _ in range(args.steps):
        state = inner.tick(state, sensory_raw={"text": args.input})


def cmd_demo_coherence(args: argparse.Namespace) -> None:
    """Run a coherence demo: Γ for swirl vs random fields, w/ and w/o boosts."""
    ledger_path = Path(args.ledger)
    ledger = OmegaLedger(ledger_path)
    contract = CoherenceContract(
        kappa=COHERENCE.kappa,
        epsilon=COHERENCE.epsilon,
    )

    n = args.n
    swirl = make_swirl_field(n)
    rand = make_random_field(n, seed=42)

    swirl_boost = add_galilean_boost(swirl, vx=0.3, vy=-0.1)
    rand_boost = add_galilean_boost(rand, vx=0.3, vy=-0.1)

    def measure(label: str, u):
        gamma_fd = contract.gamma(u)
        gamma_spec = contract.gamma_spectral_2d(u)
        payload = {
            "type": "coherence_demo",
            "label": label,
            "gamma_fd": gamma_fd,
            "gamma_spec": gamma_spec,
            "n": n,
        }
        ledger.append(payload)
        print(f"{label}: Γ_fd={gamma_fd:.4f}, Γ_spec={gamma_spec:.4f}")

    measure("swirl", swirl)
    measure("swirl_boost", swirl_boost)
    measure("random", rand)
    measure("random_boost", rand_boost)

def cmd_run_runtime(args: argparse.Namespace) -> None:
    cfg = CaelusRuntimeConfig(
        grid_size=args.grid,
        steps=args.steps,
        seed=args.seed,
        ledger_path=Path(args.ledger),
    )
    rt = CaelusRuntime(cfg)
    reply = rt.run_session(args.input)
    print(reply)

def main() -> None:
    parser = argparse.ArgumentParser("caelus")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run a short Caelus inner loop")
    p_run.add_argument("--input", required=True, help="User text input")
    p_run.add_argument("--ledger", default=str(PATHS.omega_ledger))
    p_run.add_argument("--steps", type=int, default=3)
    p_run.set_defaults(func=cmd_run)

    p_demo = sub.add_parser("demo-coherence", help="Run Γ demo (swirl vs random)")
    p_demo.add_argument("--ledger", default=str(PATHS.omega_ledger))
    p_demo.add_argument("--n", type=int, default=64, help="Grid size for test fields")
    p_demo.set_defaults(func=cmd_demo_coherence)

    p_runtime = sub.add_parser("run-runtime", help="Run Caelus via deterministic runtime wrapper")
    p_runtime.add_argument("--input", required=True, help="User text input")
    p_runtime.add_argument("--ledger", default=str(PATHS.omega_ledger))
    p_runtime.add_argument("--steps", type=int, default=3)
    p_runtime.add_argument("--grid", type=int, default=64)
    p_runtime.add_argument("---seed", type=int, default=1234)
    p_runtime.set_defaults(func=cmd_run_runtime)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
