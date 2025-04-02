import itertools

from benchmarks_utils import AIHeuristic, AIMode, run_benchmark

board_sizes = [6, 8]
num_runs = 3
baseline_config = {
    "mode": AIMode.MINIMAX,
    "depth": 1,
    "heuristic": AIHeuristic.COIN_PARITY,
}

baseline_times = {}

print("Running baseline benchmarks...")
for size in board_sizes:
    run_times = []
    for run in range(num_runs):
        time, moves = run_benchmark(
            size,
            baseline_config["depth"],
            baseline_config["mode"],
            baseline_config["heuristic"],
            f"Baseline size {size} run {run+1}",
        )
        if time:
            run_times.append(time)

    if run_times:
        baseline_times[size] = sum(run_times) / len(run_times)
        print(f"Size {size} baseline avg: {baseline_times[size]:.4f}s")

# Save baseline for other experiments
import json

with open("baseline_times.json", "w") as f:
    json.dump(baseline_times, f)
