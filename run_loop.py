
from __future__ import annotations

import json
import subprocess
import sys
import uuid
from pathlib import Path

import numpy as np

from caelus.math_core.coherence import CoherenceContract
from caelus.math_core.ufe import UFEStepper
from caelus.agent.loops import CaelusInnerLoop, make_initial_state
from caelus.ledger.omega_ledger import OmegaLedger
from phase_loom.analysis import generate_report_for_session

def run_loop(ticks: int, session_dir: Path) -> Path:
    """Run a few inner-loop ticks and check Ω-ledger structure."""
    session_dir.mkdir(parents=True, exist_ok=True)
    ledger_path = session_dir / "omega.log"
    ledger = OmegaLedger(ledger_path)

    contract = CoherenceContract()
    stepper = UFEStepper(contract)
    inner = CaelusInnerLoop(stepper=stepper, contract=contract, ledger=ledger)

    np.random.seed(1234)
    state = make_initial_state((16, 16), contract)

    for i in range(ticks):
        print(f"Running tick {i+1}/{ticks}...")
        state = inner.tick(state, sensory_raw={"text": f"tick {i}"})

    print(f"Loop complete. Ledger written to {ledger_path}")
    return ledger_path

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_loop.py <ticks>")
        sys.exit(1)

    try:
        num_ticks = int(sys.argv[1])
    except ValueError:
        print("Error: <ticks> must be an integer")
        sys.exit(1)
    
    session_id = str(uuid.uuid4())
    
    # The ledger files are stored in the `ledgers` directory.
    sessions_dir = Path("ledgers")
    session_dir = sessions_dir / session_id
    
    # Run the simulation
    ledger_path = run_loop(num_ticks, session_dir)
    
    # Generate the report automatically
    print(f"Generating report for session {session_id}...")
    try:
        generate_report_for_session(session_id, ledger_path)
        print("Report and graphs generated successfully.")
    except Exception as e:
        print(f"An error occurred during report generation: {e}")
