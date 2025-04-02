import subprocess
import re
from enum import Enum


class AIMode(Enum):
    MINIMAX = "minimax"
    ALPHABETA = "ab"


class AIHeuristic(Enum):
    CORNERS_CAPTURED = "corners_captured"
    COIN_PARITY = "coin_parity"
    MOBILITY = "mobility"
    ALL_IN_ONE = "all_in_one"


time_pattern = re.compile(r"Time taken: (\d+\.\d+) seconds")


def run_benchmark(size, depth, mode, heuristic, run_name=None):
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
        result = subprocess.run(cmd, capture_output=True, text=True)
        output = result.stdout
        matches = time_pattern.findall(output)

        if matches:
            move_times = [float(time_str) for time_str in matches]
            avg_move_time = sum(move_times) / len(move_times)
            if run_name:
                print(
                    f"  {run_name}: Avg move time: {avg_move_time:.4f}s ({len(move_times)} moves)"
                )
            return avg_move_time, len(move_times)
        return None, 0
    except Exception as e:
        print(f"Error running benchmark: {e}")
        return None, 0


def save_results(results, filename):
    import csv

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

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
