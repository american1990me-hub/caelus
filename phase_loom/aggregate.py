
import json
from pathlib import Path
import numpy as np

# Define the directories and the output file
LEDGERS_DIR = Path("ledgers")
REPORTS_DIR = Path("phaseloom-ui/public/reports")
OUTPUT_FILE = REPORTS_DIR / "density_map.json"

# Define the grid parameters
TIME_BINS = 50  # Number of time steps in the grid
C_BINS = 100    # Number of complexity bins

def aggregate_sessions_for_density_map():
    """Scans all session logs and creates a 2D density map of trajectories."""
    REPORTS_DIR.mkdir(exist_ok=True)
    all_trajectories = []

    # 1. Collect all session trajectories
    for session_dir in LEDGERS_DIR.iterdir():
        if session_dir.is_dir():
            ledger_file = session_dir / "omega.log"
            if ledger_file.exists():
                current_trajectory = []
                with open(ledger_file, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            payload = entry.get("payload", {})
                            if payload.get("type") == "inner_tick":
                                diagnostics = payload.get("diagnostics", {})
                                c_value = diagnostics.get("C")
                                if c_value is not None:
                                    current_trajectory.append(c_value)
                        except json.JSONDecodeError:
                            continue  # Ignore malformed lines
                if current_trajectory:
                    all_trajectories.append(current_trajectory)
    
    if not all_trajectories:
        print("No valid session data found.")
        return

    # 2. Determine the bounds for the grid
    max_time = max(len(t) for t in all_trajectories)
    # To create a stable visualization, we'll use fixed bounds for C for now.
    min_c, max_c = 340, 360

    # 3. Create the density grid (our Z-axis data)
    density_grid = np.zeros((C_BINS, max_time))
    c_step = (max_c - min_c) / C_BINS

    for trajectory in all_trajectories:
        for time_step, c_value in enumerate(trajectory):
            if min_c <= c_value < max_c:
                c_bin = int((c_value - min_c) / c_step)
                if time_step < max_time:
                    density_grid[c_bin, time_step] += 1
    
    # 4. Prepare data for JSON output
    # The X axis is time
    x_axis = list(range(max_time))
    # The Y axis represents the complexity 'C' bins
    y_axis = (np.linspace(min_c, max_c, C_BINS)).tolist()
    # The Z axis is the density data
    z_axis = density_grid.tolist()

    output_data = {
        "x": x_axis,
        "y": y_axis,
        "z": z_axis,
        "name": "Trajectory Density",
        "type": "surface"
    }

    # 5. Save the aggregated data
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f)
    
    print(f"Density map generated and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    aggregate_sessions_for_density_map()
