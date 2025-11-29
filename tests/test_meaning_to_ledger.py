from __future__ import annotations

import json
from pathlib import Path

from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig
from caelus.agent.sensory import reset_sensory_engines


def test_meaning_structures_logged_to_omega(tmp_path: Path) -> None:
    reset_sensory_engines()
    ledger_path = tmp_path / "omega_meaning.log"

    cfg = CaelusRuntimeConfig(
        grid_size=16,
        steps=1,
        seed=123,
        ledger_path=ledger_path,
    )
    rt = CaelusRuntime(cfg)
    rt.run_session("define coherence field")

    lines = [ln for ln in ledger_path.read_text().splitlines() if ln.strip()]
    # Expect at least: genesis, session_start, one inner_tick, session_end
    assert len(lines) >= 4

    # Find an inner_tick entry
    inner = None
    for ln in lines:
        data = json.loads(ln)
        if data["payload"].get("type") == "inner_tick":
            inner = data["payload"]
            break

    assert inner is not None

    sensory = inner["sensory"]
    utter = sensory["utterance"]
    assert utter["intent"]["type"] == "DEFINE"
    assert "sem:coherence_field" in utter["intent"]["concepts"]

    # Semantic graph snapshot present
    sem = sensory["semantic"]
    assert "nodes" in sem and "edges" in sem

    # Argument graph snapshot present
    arg = sensory["argument"]
    assert "nodes" in arg and "edges" in arg
