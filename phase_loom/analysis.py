
import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from phase_loom.metrics import compute_gate5_metrics, compute_cace_metrics

REPORTS_DIR = Path("phaseloom-ui/public/reports")

def generate_report_for_session(session_id: str, ledger_path: Path) -> dict:
    """Analyzes a session ledger to generate a comprehensive report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with open(ledger_path, 'r') as f:
            session_data = [json.loads(line) for line in f]
    except FileNotFoundError:
        return {"error": "Ledger file not found."}
    except json.JSONDecodeError:
        return {"error": "Could not decode JSON."}

    main_graph = nx.DiGraph()
    turns_data = []
    turn_index = 0

    for entry in session_data:
        # Corrected: The log entries have a 'payload' key, not 'data'.
        payload = entry.get("payload", {})

        # We are interested in the 'inner_tick' entries for the graph.
        if payload.get("type") == "inner_tick":
            node_data = payload.get("diagnostics", {})
            main_graph.add_node(turn_index, **node_data)
            
            if turn_index > 0:
                main_graph.add_edge(turn_index - 1, turn_index)
            
            turns_data.append(payload)
            turn_index += 1

    image_name = f"{session_id}.jpg"
    image_path = REPORTS_DIR / image_name
    
    try:
        render_main_graph(main_graph, image_path)
    except Exception as e:
        return {"error": f"Failed to save main graph: {e}"}

    gate5_metrics = compute_gate5_metrics(session_id, turns_data)
    cace_metrics = compute_cace_metrics([])

    report = {
        "summary": {
            "session_id": session_id,
            "total_payloads": len(session_data),
            "num_nodes": main_graph.number_of_nodes(),
            "num_edges": main_graph.number_of_edges(),
            "num_sessions": 1,
            "num_turns": len(turns_data),
        },
        "image_url": f"/reports/{image_name}",
        "gate5": gate5_metrics,
        "cace": cace_metrics,
    }

    return report

def render_main_graph(graph: nx.DiGraph, image_path: Path):
    """Renders the main conversation graph."""
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(graph, seed=42)
    nx.draw(graph, pos, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.title("Conversation Graph")
    
    plt.savefig(image_path, format="JPG", dpi=150)
    plt.close()
