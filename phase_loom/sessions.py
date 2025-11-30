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
    """Discovers all sessions by looking for omega.log files in subdirectories."""
    omega_dir.mkdir(parents=True, exist_ok=True)
    sessions: List[SessionInfo] = []

    # Search for omega.log files in all subdirectories
    for p in sorted(omega_dir.glob("**/omega.log")):
        # The session ID is the name of the parent directory
        sid = p.parent.name
        sessions.append(SessionInfo(session_id=sid, path=p))
    return sessions


def load_fabric_for_session(omega_dir: Path, session_id: str) -> Dict[str, Any]:
    """Loads the data for a specific session."""
    # The path is now a subdirectory containing omega.log
    path = omega_dir / session_id / "omega.log"
    if not path.exists():
        raise FileNotFoundError(f"No ledger for session_id={session_id}")

    fabric = build_fabric_from_omega(
        path, fabric_id=session_id, payload_limit=200
    )  # Limit the payload
    return fabric.to_dict()
