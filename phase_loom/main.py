from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import load_config
from .sessions import discover_sessions, load_fabric_for_session
from .metrics_api import router as metrics_router


cfg = load_config()
app = FastAPI(title="PhaseLoom API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics_router)


@app.get("/api/sessions")
async def list_sessions():
    sessions = discover_sessions(cfg.omega_dir)
    return [
        {
            "session_id": s.session_id,
            "path": str(s.path),
        }
        for s in sessions
    ]


@app.get("/api/fabric/{session_id}")
async def get_fabric(session_id: str):
    try:
        fabric = load_fabric_for_session(cfg.omega_dir, session_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    return fabric
