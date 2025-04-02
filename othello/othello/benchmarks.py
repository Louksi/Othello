import subprocess
import csv
import re
import itertools
from enum import Enum


# Define the AI modes and heuristics as in your code
class AIMode(Enum):
    MINIMAX = "minimax"
    ALPHABETA = "ab"


class AIHeuristic(Enum):
    CORNERS_CAPTURED = "corners_captured"
    COIN_PARITY = "coin_parity"
    MOBILITY = "mobility"
    ALL_IN_ONE = "all_in_one"


# Configuration parameters to test
board_sizes = [6, 8]
ai_depths = [1, 2, 3]
ai_modes = [AIMode.MINIMAX, AIMode.ALPHABETA]
ai_heuristics = [
    AIHeuristic.CORNERS_CAPTURED,
    AIHeuristic.COIN_PARITY,
    AIHeuristic.MOBILITY,
    AIHeuristic.ALL_IN_ONE,
]

# Baseline configuration (minimax depth 0 with coin_parity)
baseline_mode = AIMode.MINIMAX
baseline_depth = 1
baseline_heuristic = AIHeuristic.COIN_PARITY

# Number of runs for each configuration
num_runs = 3

# Results will be stored here
results = []

# Regular expression to extract time from output
time_pattern = re.compile(r"Time taken: (\d+\.\d+) seconds")


# Function to run a benchmark and collect times
def run_benchmark(size, depth, mode, heuristic, run_name):
    cmd = [
        "othello",
        "--benchmark",
        "-a",
        "-s",
        str(size),
        "--ai-depth",
        str(depth),
        "--ai-mode",
        mode.value,
        "--ai-heuristic",
        heuristic.value,
    ]

    try:
        # Run the command and capture the output
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout

        # Extract all time measurements from the output
        matches = time_pattern.findall(output)
        if matches:
            # Calculate average of all move times
            move_times = [float(time_str) for time_str in matches]
            avg_move_time = sum(move_times) / len(move_times)
            print(
                f"  {run_name}: Average move time: {avg_move_time:.4f} seconds ({len(move_times)} moves)"
            )
            return avg_move_time, len(move_times)
        else:
            print(f"  {run_name}: Could not extract times from output")
            return None, 0
    except Exception as e:
        print(f"  Error running benchmark: {e}")
        return None, 0


# First, run the baseline configuration to get reference times
print(f"Running baseline benchmark (minimax depth 0 with coin_parity)...")
baseline_times = {}

for size in board_sizes:
    baseline_runs = []
    for run in range(num_runs):
        avg_time, num_moves = run_benchmark(
            size,
            baseline_depth,
            baseline_mode,
            baseline_heuristic,
            f"Baseline (size {size}) run {run+1}",
        )
        if avg_time:
            baseline_runs.append(avg_time)

    if baseline_runs:
        baseline_times[size] = sum(baseline_runs) / len(baseline_runs)
    else:
        baseline_times[size] = None
        print(f"  Warning: Could not get baseline times for board size {size}")

# Now run all the configuration combinations
for size, depth, mode, heuristic in itertools.product(
    board_sizes, ai_depths, ai_modes, ai_heuristics
):
    # Skip the baseline configuration since we've already tested it
    if (
        depth == baseline_depth
        and mode == baseline_mode
        and heuristic == baseline_heuristic
    ):
        continue

    config_name = f"s{size}_d{depth}_{mode.value}_{heuristic.value}"
    print(f"Running benchmark for: {config_name}")

    config_times = []
    total_moves = 0

    for run in range(num_runs):
        avg_time, num_moves = run_benchmark(
            size, depth, mode, heuristic, f"Run {run+1}"
        )
        if avg_time:
            config_times.append(avg_time)
            total_moves += num_moves

    # Calculate average time if we have any successful runs
    if config_times:
        avg_time = sum(config_times) / len(config_times)
        baseline_time = baseline_times.get(size)
        speedup = baseline_time / avg_time if baseline_time and avg_time else None
    else:
        avg_time = None
        speedup = None

    # Store the results
    results.append(
        {
            "board_size": size,
            "ai_depth": depth,
            "ai_mode": mode.value,
            "ai_heuristic": heuristic.value,
            "avg_time": avg_time,
            "baseline_time": baseline_times.get(size),
            "speedup_factor": speedup,
            "num_runs": len(config_times),
            "avg_moves_per_run": total_moves / len(config_times) if config_times else 0,
        }
    )

# Add baseline results to the results list
for size in board_sizes:
    results.append(
        {
            "board_size": size,
            "ai_depth": baseline_depth,
            "ai_mode": baseline_mode.value,
            "ai_heuristic": baseline_heuristic.value,
            "avg_time": baseline_times.get(size),
            "baseline_time": baseline_times.get(size),
            "speedup_factor": 1.0,  # Baseline compared to itself is 1.0
            "num_runs": num_runs,
            "avg_moves_per_run": 0,  # We don't track this for baseline
        }
    )

# Write results to CSV
csv_filename = "othello_benchmark_results.csv"
fieldnames = [
    "board_size",
    "ai_depth",
    "ai_mode",
    "ai_heuristic",
    "avg_time",
    "baseline_time",
    "speedup_factor",
    "num_runs",
    "avg_moves_per_run",
]

with open(csv_filename, "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)

print(f"\nResults saved to {csv_filename}")
