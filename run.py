from __future__ import annotations
import sys
import uuid
from datetime import datetime
from pathlib import Path
from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig

if len(sys.argv) > 1:
    message = sys.argv[1]
else:
    message = "hello world"

# Generate a unique session ID using a timestamp and a UUID
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
unique_id = str(uuid.uuid4())[:8]
session_id = f"session_{timestamp}_{unique_id}"

# Define the directory for logs and ensure it exists
log_dir = Path("omega_logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Construct the unique ledger path
ledger_path = log_dir / f"{session_id}.log"

cfg = CaelusRuntimeConfig(
    grid_size=16,
    steps=2,
    seed=42,
    ledger_path=ledger_path,
)
rt = CaelusRuntime(cfg)
reply = rt.run_session(message)
print(reply)