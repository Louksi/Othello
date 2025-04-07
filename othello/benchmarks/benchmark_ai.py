import subprocess
import re
import csv
from enum import Enum
from itertools import product
import time
import json
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt


class AIMode(Enum):
    MINIMAX = "minimax"
    ALPHABETA = "ab"


class AIHeuristic(Enum):
    CORNERS_CAPTURED = "corners_captured"
    COIN_PARITY = "coin_parity"
    MOBILITY = "mobility"
    STABILITY = "stability"
    ALL_IN_ONE = "all_in_one"


class AIDepth(Enum):
    SHALLOW = 2
    MEDIUM = 4
    DEEP = 6


# Patterns to extract game information
time_pattern = re.compile(r"Time taken: (\d+\.\d+) seconds")
score_pattern = re.compile(r"Final score: X:(\d+), O:(\d+)")
move_pattern = re.compile(r"Total moves: (\d+)")


def run_match(black_config, white_config, board_size=8, num_games=10):
    """Run a match between two AI configurations"""
    results = {
        "black_wins": 0,
        "white_wins": 0,
        "draws": 0,
        "black_avg_time": 0,
        "white_avg_time": 0,
        "total_moves": 0,
    }

    black_times = []
    white_times = []

    for game in range(num_games):
        cmd = [
            "othello",
            "--benchmark",
            "-a",
            "A",  # Both players are AI
            "-s",
            str(board_size),
            "--ai-depth",
            str(black_config["depth"]),
            "--ai-mode",
            black_config["mode"].value,
            "--ai-heuristic",
            black_config["heuristic"].value,
            "--ai-color",
            "X",  # Black is first config
            "--ai-depth",
            str(white_config["depth"]),  # White config
            "--ai-mode",
            white_config["mode"].value,
            "--ai-heuristic",
            white_config["heuristic"].value,
            "--ai-color",
            "O",  # White is second config
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            output = result.stdout

            # Parse results
            time_matches = time_pattern.findall(output)
            score_match = score_pattern.search(output)
            move_match = move_pattern.search(output)

            if score_match and time_matches and move_match:
                black_score = int(score_match.group(1))
                white_score = int(score_match.group(2))
                total_moves = int(move_match.group(1))

                # Split times between players (alternating moves)
                black_times.extend(
                    [float(t) for i, t in enumerate(time_matches) if i % 2 == 0]
                )
                white_times.extend(
                    [float(t) for i, t in enumerate(time_matches) if i % 2 == 1]
                )

                if black_score > white_score:
                    results["black_wins"] += 1
                elif white_score > black_score:
                    results["white_wins"] += 1
                else:
                    results["draws"] += 1

                results["total_moves"] += total_moves

        except Exception as e:
            print(f"Error running game {game+1}: {e}")
            continue

    # Calculate averages
    if black_times:
        results["black_avg_time"] = sum(black_times) / len(black_times)
    if white_times:
        results["white_avg_time"] = sum(white_times) / len(white_times)

    return results


def run_heuristic_benchmark():
    """Benchmark different heuristics against each other"""
    board_size = 8
    depth = AIDepth.MEDIUM.value
    mode = AIMode.ALPHABETA
    num_games = 20

    heuristics = list(AIHeuristic)
    results = []

    print("Running heuristic benchmark...")

    # Test each heuristic against every other heuristic
    for black_heuristic, white_heuristic in product(heuristics, repeat=2):
        if black_heuristic == white_heuristic:
            continue  # Skip same vs same

        black_config = {"mode": mode, "depth": depth, "heuristic": black_heuristic}

        white_config = {"mode": mode, "depth": depth, "heuristic": white_heuristic}

        print(
            f"Testing {black_heuristic.value} (Black) vs {white_heuristic.value} (White)..."
        )
        match_results = run_match(black_config, white_config, board_size, num_games)

        results.append(
            {
                "black_heuristic": black_heuristic.value,
                "white_heuristic": white_heuristic.value,
                "black_wins": match_results["black_wins"],
                "white_wins": match_results["white_wins"],
                "draws": match_results["draws"],
                "black_avg_time": match_results["black_avg_time"],
                "white_avg_time": match_results["white_avg_time"],
                "total_moves": match_results["total_moves"],
                "win_rate": match_results["black_wins"] / num_games,
            }
        )

    # Save results
    df = pd.DataFrame(results)
    df.to_csv("heuristic_benchmark_results.csv", index=False)

    # Generate visualization
    plot_heuristic_results(df)


def plot_heuristic_results(df):
    """Visualize heuristic benchmark results"""
    plt.figure(figsize=(12, 8))

    # Win rate comparison
    win_rates = df.groupby("black_heuristic")["win_rate"].mean().sort_values()
    win_rates.plot(kind="bar", color="skyblue")
    plt.title("Win Rate by Heuristic (as Black)")
    plt.ylabel("Win Rate")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("heuristic_win_rates.png")
    plt.close()

    # Time comparison
    plt.figure(figsize=(12, 8))
    time_data = df[["black_heuristic", "black_avg_time"]].rename(
        columns={"black_heuristic": "heuristic", "black_avg_time": "avg_time"}
    )
    time_data.groupby("heuristic")["avg_time"].mean().sort_values().plot(
        kind="bar", color="lightgreen"
    )
    plt.title("Average Move Time by Heuristic")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("heuristic_times.png")
    plt.close()


def run_algorithm_benchmark():
    """Benchmark minimax vs alpha-beta"""
    board_size = 8
    depth = AIDepth.MEDIUM.value
    heuristic = AIHeuristic.CORNERS_CAPTURED
    num_games = 20

    print("Running algorithm benchmark (Minimax vs Alpha-Beta)...")

    # Test minimax vs alpha-beta
    configs = [
        {"mode": AIMode.MINIMAX, "depth": depth, "heuristic": heuristic},
        {"mode": AIMode.ALPHABETA, "depth": depth, "heuristic": heuristic},
    ]

    results = []

    for black_config, white_config in product(configs, repeat=2):
        if black_config["mode"] == white_config["mode"]:
            continue  # Skip same vs same

        print(
            f"Testing {black_config['mode'].value} (Black) vs {white_config['mode'].value} (White)..."
        )
        match_results = run_match(black_config, white_config, board_size, num_games)

        results.append(
            {
                "black_algorithm": black_config["mode"].value,
                "white_algorithm": white_config["mode"].value,
                "black_wins": match_results["black_wins"],
                "white_wins": match_results["white_wins"],
                "draws": match_results["draws"],
                "black_avg_time": match_results["black_avg_time"],
                "white_avg_time": match_results["white_avg_time"],
                "total_moves": match_results["total_moves"],
                "win_rate": match_results["black_wins"] / num_games,
            }
        )

    # Save results
    df = pd.DataFrame(results)
    df.to_csv("algorithm_benchmark_results.csv", index=False)

    # Generate visualization
    plot_algorithm_results(df)


def plot_algorithm_results(df):
    """Visualize algorithm benchmark results"""
    plt.figure(figsize=(10, 6))

    # Win rate comparison
    win_rates = df.groupby("black_algorithm")["win_rate"].mean()
    win_rates.plot(kind="bar", color=["skyblue", "lightgreen"])
    plt.title("Win Rate by Algorithm (as Black)")
    plt.ylabel("Win Rate")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("algorithm_win_rates.png")
    plt.close()

    # Time comparison
    plt.figure(figsize=(10, 6))
    time_data = df[["black_algorithm", "black_avg_time"]].rename(
        columns={"black_algorithm": "algorithm", "black_avg_time": "avg_time"}
    )
    time_data.groupby("algorithm")["avg_time"].mean().plot(
        kind="bar", color=["skyblue", "lightgreen"]
    )
    plt.title("Average Move Time by Algorithm")
    plt.ylabel("Time (seconds)")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("algorithm_times.png")
    plt.close()


if __name__ == "__main__":
    # Run all benchmarks
    run_heuristic_benchmark()
    run_algorithm_benchmark()

    print(
        "Benchmarking complete! Results saved to CSV files and visualizations generated."
    )
