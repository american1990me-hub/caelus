import argparse
import json
import uuid
from pathlib import Path

from caelus.conversation.testing import run_scenario_with_metrics
from caelus.ledger.signed_ledger import SignedOmegaLedger


def main():
    parser = argparse.ArgumentParser(description="Run a Caelus conversation scenario.")
    parser.add_argument("scenario_path", help="Path to the conversation scenario JSON file.")
    parser.add_argument("--session-id", help="Provide a session ID.")
    parser.add_argument("--ledger-path", default="omega_logs/omega_signed.log", help="Path to the Omega ledger file.")
    args = parser.parse_args()

    # Generate a session ID if not provided
    session_id = args.session_id
    if session_id is None:
        session_id = f"conv_{uuid.uuid4().hex[:8]}"

    # Initialize the ledger
    ledger = SignedOmegaLedger(path=Path(args.ledger_path))

    # Run the scenario
    metrics = run_scenario_with_metrics(
        path=args.scenario_path,
        ledger=ledger,
        session_id=session_id,
    )

    # Output the metrics
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
