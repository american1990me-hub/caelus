
from __future__ import annotations
import asyncio
import subprocess
import uuid
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .config import load_config
from .sessions import discover_sessions
from .analysis import generate_report_for_session

cfg = load_config()
app = FastAPI(title="PhaseLoom API", version="0.1.0")

# Global variable to hold the Caelus subprocess
caelus_process = None

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/caelus/start")
async def start_caelus_session():
    global caelus_process
    if caelus_process is not None and caelus_process.poll() is None:
        raise HTTPException(status_code=400, detail="A Caelus session is already running.")

    session_id = str(uuid.uuid4())
    ledger_path = Path("ledgers") / session_id / "omega.log"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    command = [
        "python", 
        "run_conversation_scenario.py", 
        "tests/fixtures/conv_scenarios/noetica_mix.json",
        "--session-id", session_id,
        "--ledger-path", str(ledger_path),
    ]
    
    try:
        # Create the subprocess and capture stderr
        caelus_process = await asyncio.create_subprocess_exec(
            *command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Caelus session: The command 'python' or the script 'run_conversation_scenario.py' was not found."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while starting the Caelus session: {e}"
        )

    # Wait for a short period to see if there's an immediate error
    await asyncio.sleep(1)
    
    # Check if the process has exited with an error
    if caelus_process.returncode is not None and caelus_process.returncode != 0:
        stderr = await caelus_process.stderr.read()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start Caelus session: {stderr.decode().strip()}"
        )

    return {"message": f"Caelus session {session_id} started successfully."}

@app.post("/api/caelus/stop")
async def stop_caelus_session():
    global caelus_process
    if caelus_process is None or caelus_process.poll() is not None:
        raise HTTPException(status_code=404, detail="No active Caelus session found.")
    
    caelus_process.terminate()
    await caelus_process.wait()
    caelus_process = None
    return {"message": "Caelus session stopped."}

@app.websocket("/ws/caelus")
async def websocket_caelus_log(websocket: WebSocket):
    global caelus_process
    await websocket.accept()

    if caelus_process is None or caelus_process.stdout is None:
        await websocket.send_text("No active Caelus process to stream logs from.")
        await websocket.close()
        return

    try:
        while True:
            line = await caelus_process.stdout.readline()
            if not line:
                break
            await websocket.send_text(line.decode('utf-8').strip())
        await websocket.send_text("Caelus process finished.")
    except WebSocketDisconnect:
        print("Client disconnected from Caelus log stream.")
    except Exception as e:
        print(f"An error occurred in the WebSocket: {e}")
    finally:
        await websocket.close()


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


@app.get("/api/sessions/{session_id}/report")
async def get_session_report(session_id: str):
    try:
        ledger_path = cfg.omega_dir / session_id / "omega.log"
        report = generate_report_for_session(session_id, ledger_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    return report
