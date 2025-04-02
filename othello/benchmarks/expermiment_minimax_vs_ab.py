import itertools
import json

from benchmarks_utils import AIHeuristic, AIMode, run_benchmark, save_results

# Load baseline
with open("baseline_times.json") as f:
    baseline_times = json.load(f)

board_sizes = [6, 8]
depths = [1, 2, 3]
heuristics = [AIHeuristic.ALL_IN_ONE]  # Focus on one heuristic for this comparison
num_runs = 3

results = []

print("Comparing Minimax vs Alpha-Beta...")
for size, depth, heuristic, mode in itertools.product(
    board_sizes, depths, heuristics, [AIMode.MINIMAX, AIMode.ALPHABETA]
):
    config_name = f"s{size}_d{depth}_{mode.value}_{heuristic.value}"
    print(f"Running: {config_name}")

    run_times = []
    total_moves = 0

    for run in range(num_runs):
        time, moves = run_benchmark(size, depth, mode, heuristic, f"Run {run+1}")
        if time:
            run_times.append(time)
            total_moves += moves

    if run_times:
        avg_time = sum(run_times) / len(run_times)
        speedup = float(baseline_times[str(size)]) / avg_time

        results.append(
            {
                "board_size": size,
                "ai_depth": depth,
                "ai_mode": mode.value,
                "ai_heuristic": heuristic.value,
                "avg_time": avg_time,
                "baseline_time": float(baseline_times[str(size)]),
                "speedup_factor": speedup,
                "num_runs": len(run_times),
                "avg_moves_per_run": total_moves / len(run_times),
            }
        )

save_results(results, "minimax_vs_ab_results.csv")
