from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

from caelus.cgf.from_omega import build_fabric_from_omega


@dataclass
class SessionInfo:
    session_id: str
    path: Path


def discover_sessions(omega_dir: Path) -> List[SessionInfo]:
    omega_dir.mkdir(parents=True, exist_ok=True)
    sessions: List[SessionInfo] = []

    for p in sorted(omega_dir.glob("*.log")):
        sid = p.stem
        sessions.append(SessionInfo(session_id=sid, path=p))
    return sessions


def load_fabric_for_session(omega_dir: Path, session_id: str) -> Dict[str, Any]:
    path = omega_dir / f"{session_id}.log"
    if not path.exists():
        raise FileNotFoundError(f"No ledger for session_id={session_id}")

    fabric = build_fabric_from_omega(path, fabric_id=session_id)
    return fabric.to_dict()
