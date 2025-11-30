
import os
import matplotlib.pyplot as plt
import numpy as np

# All generated images should be saved to the UI's public reports directory
REPORTS_DIR = "phaseloom-ui/public/reports"

def compute_gate5_metrics(session_id: str, turns_data: list) -> dict:
    if not turns_data:
        return {"turns": [], "image_url": ''}

    # Generate the plot and get the image URL
    image_url = render_gate5_graph(session_id, turns_data)

    # The rest of the metrics calculation remains the same, but using correct keys
    gamma_series = [t.get("gamma_new") for t in turns_data]
    c_self_series = [t.get("diagnostics", {}).get("C") for t in turns_data]
    
    return {
        "turns": turns_data,
        "image_url": image_url,
        "summary": {
            "gamma_final": gamma_series[-1] if gamma_series else None,
            "c_self_final": c_self_series[-1] if c_self_series else None,
        }
    }

def render_gate5_graph(session_id: str, turns_data: list) -> str:
    """Renders the Gate 5 graph and saves it to the public reports directory."""
    os.makedirs(REPORTS_DIR, exist_ok=True)

    # The turn index is simply the position in the list
    turn_indices = range(len(turns_data))
    
    # Correctly extract Gamma and C_self from the payload
    gamma_values = [t.get("gamma_new") for t in turns_data]
    c_self_values = [t.get("diagnostics", {}).get("C") for t in turns_data]

    plt.figure(figsize=(10, 6))
    plt.plot(turn_indices, gamma_values, label='Gamma')
    plt.plot(turn_indices, c_self_values, label='C_self')
    plt.xlabel("Turn Index")
    plt.ylabel("Value")
    plt.title(f"Gate 5 Metrics for Session {session_id}")
    plt.legend()
    plt.grid(True)

    # Save the image to the correct directory and use a consistent extension
    image_name = f"{session_id}_gate5.jpg"
    image_path = os.path.join(REPORTS_DIR, image_name)
    plt.savefig(image_path, format="JPG", dpi=100)
    plt.close()

    # Return the public URL path for the frontend
    return f"/reports/{image_name}"

def compute_cace_metrics(cace_data: list) -> dict:
    # This function remains unchanged
    if not cace_data:
        return {"layers": [], "summaries": [], "policy_updates": []}
    
    # Placeholder for actual CACE metrics
    return {"layers": [], "summaries": [], "policy_updates": []}
