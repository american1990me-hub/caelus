
from __future__ import annotations
import sys
from caelus.runtime.runtime import CaelusRuntime, CaelusRuntimeConfig

if len(sys.argv) > 1:
    message = sys.argv[1]
else:
    message = "hello world"

cfg = CaelusRuntimeConfig(
    grid_size=16,
    steps=2,
    seed=42,
)
rt = CaelusRuntime(cfg)
reply = rt.run_session(message)
print(reply)
