
import json
from pathlib import Path
import tempfile

from caelus.conversation.testing import run_scenario_with_metrics
from caelus.ledger.signed_ledger import SignedOmegaLedger
from caelus.cgf.from_omega import build_fabric_from_omega

with tempfile.TemporaryDirectory() as tmpdir:
    ledger_path = Path(tmpdir) / "omega_conv_cgf.log"
    ledger = SignedOmegaLedger(ledger_path)

    run_scenario_with_metrics(
        "tests/fixtures/conv_scenarios/noetica_mix.json",
        ledger=ledger,
        session_id="noetica_sess_run",
    )

    fabric = build_fabric_from_omega(ledger_path, fabric_id="fabric_conv_run")
    d = fabric.to_dict()

    conv_graph = d.get("conversation_graph", {})
    print("--- Generated Conversation Graph ---")
    print(json.dumps(conv_graph, indent=2))
    print("------------------------------------")
