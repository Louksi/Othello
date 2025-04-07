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
import os
import sys


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


# Updated patterns to match the actual output format
time_pattern = re.compile(r"Execution time: (\d+\.\d+) seconds")
score_pattern = re.compile(r"Final score - Black: (\d+), White: (\d+)")
# For moves, we'll count turn numbers since there's no explicit total
turn_pattern = re.compile(r"=== turn (\d+) ===")


def run_match(black_config, white_config, board_size=8, num_games=10):
    """Run a match between two AI configurations"""
    print(f"  Running {num_games} games with board size {board_size}...")

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
            "B",  # Both players with separate configs
            "-s",
            str(board_size),
            "--ai-depth",
            str(black_config["depth"]),
            "--ai-mode",
            black_config["mode"].value,
            "--ai-heuristic",
            black_config["heuristic"].value,
            "--white-ai-depth",
            str(white_config["depth"]),
            "--white-ai-mode",
            white_config["mode"].value,
            "--white-ai-heuristic",
            white_config["heuristic"].value,
        ]

        try:
            print(f"    Game {game+1}/{num_games}: Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"    Game {game+1} failed with error code {result.returncode}")
                print(f"    Error output: {result.stderr}")
                continue

            output = result.stdout

            # Debug: Print some of the output to verify
            print(f"    Output preview: {output[:100]}...")

            # Parse results
            time_matches = time_pattern.findall(output)
            score_match = score_pattern.search(output)
            turn_matches = turn_pattern.findall(output)

            # Calculate total moves from the highest turn number
            total_moves = 0
            if turn_matches:
                total_moves = max(int(turn) for turn in turn_matches)

            if not time_matches:
                print("    No time information found in output")
                # Debug: Print a segment of the output to see what the actual format is
                print("    Output sample for time pattern debugging:")
                time_debug = re.findall(r".*time.*", output, re.IGNORECASE)
                if time_debug:
                    print(f"    Time-related lines: {time_debug[:5]}")

            if not score_match:
                print("    No score information found in output")
                # Debug: Print a segment of the output to see what the actual format is
                print("    Output sample for score pattern debugging:")
                score_debug = re.findall(r".*score.*", output, re.IGNORECASE)
                if score_debug:
                    print(f"    Score-related lines: {score_debug}")

            if not turn_matches:
                print("    No turn information found in output")
                # Debug: Print a segment of the output to see what the actual format is
                print("    Output sample for turn pattern debugging:")
                turn_debug = re.findall(r".*turn.*", output, re.IGNORECASE)
                if turn_debug:
                    print(f"    Turn-related lines: {turn_debug[:5]}")

            if score_match and time_matches:
                black_score = int(score_match.group(1))
                white_score = int(score_match.group(2))

                print(
                    f"    Game {game+1} result: Black {black_score} - White {white_score}, Moves: {total_moves}"
                )

                # Split times between players (alternating moves)
                # Black usually goes first in Othello
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
            else:
                print("    Could not parse all required information from game output")

        except Exception as e:
            print(f"    Error running game {game+1}: {str(e)}")
            continue

    # Calculate averages
    if black_times:
        results["black_avg_time"] = sum(black_times) / len(black_times)
    if white_times:
        results["white_avg_time"] = sum(white_times) / len(white_times)

    print(
        f"  Match summary: Black wins: {results['black_wins']}, White wins: {results['white_wins']}, Draws: {results['draws']}"
    )
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
                "win_rate": (
                    match_results["black_wins"] / num_games if num_games > 0 else 0
                ),
            }
        )

    # Save results - with explicit path for visibility
    csv_path = os.path.join(os.getcwd(), "heuristic_benchmark_results.csv")
    print(f"Saving heuristic results to: {csv_path}")

    try:
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False)
        print(f"Successfully saved heuristic results to CSV")

        # Also save as JSON as a backup format
        json_path = os.path.join(os.getcwd(), "heuristic_benchmark_results.json")
        df.to_json(json_path, orient="records")
        print(f"Also saved results as JSON to: {json_path}")

        # Generate visualization
        plot_heuristic_results(df)
    except Exception as e:
        print(f"Error saving heuristic results: {str(e)}")

        # Fallback: Try saving raw results
        fallback_path = os.path.join(os.getcwd(), "heuristic_results_raw.json")
        try:
            with open(fallback_path, "w") as f:
                json.dump(results, f)
            print(f"Saved raw results to: {fallback_path}")
        except Exception as e2:
            print(f"Failed to save even raw results: {str(e2)}")


def plot_heuristic_results(df):
    """Visualize heuristic benchmark results"""
    try:
        print("Generating heuristic plots...")
        plt.figure(figsize=(12, 8))

        # Win rate comparison
        win_rates = df.groupby("black_heuristic")["win_rate"].mean().sort_values()
        win_rates.plot(kind="bar", color="skyblue")
        plt.title("Win Rate by Heuristic (as Black)")
        plt.ylabel("Win Rate")
        plt.xticks(rotation=45)
        plt.tight_layout()

        plot_path = os.path.join(os.getcwd(), "heuristic_win_rates.png")
        print(f"Saving win rate plot to: {plot_path}")
        plt.savefig(plot_path)
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

        time_plot_path = os.path.join(os.getcwd(), "heuristic_times.png")
        print(f"Saving time plot to: {time_plot_path}")
        plt.savefig(time_plot_path)
        plt.close()
        print("Plots generated successfully")

    except Exception as e:
        print(f"Error generating plots: {str(e)}")
        import traceback

        traceback.print_exc()


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
                "win_rate": (
                    match_results["black_wins"] / num_games if num_games > 0 else 0
                ),
            }
        )

    # Save results with explicit path
    csv_path = os.path.join(os.getcwd(), "algorithm_benchmark_results.csv")
    print(f"Saving algorithm results to: {csv_path}")

    try:
        df = pd.DataFrame(results)
        df.to_csv(csv_path, index=False)
        print(f"Successfully saved algorithm results to CSV")

        # Also save as JSON as a backup format
        json_path = os.path.join(os.getcwd(), "algorithm_benchmark_results.json")
        df.to_json(json_path, orient="records")
        print(f"Also saved results as JSON to: {json_path}")

        # Generate visualization
        plot_algorithm_results(df)
    except Exception as e:
        print(f"Error saving algorithm results: {str(e)}")

        # Fallback: Try saving raw results
        fallback_path = os.path.join(os.getcwd(), "algorithm_results_raw.json")
        try:
            with open(fallback_path, "w") as f:
                json.dump(results, f)
            print(f"Saved raw results to: {fallback_path}")
        except Exception as e2:
            print(f"Failed to save even raw results: {str(e2)}")


def plot_algorithm_results(df):
    """Visualize algorithm benchmark results"""
    try:
        print("Generating algorithm plots...")
        plt.figure(figsize=(10, 6))

        # Win rate comparison
        win_rates = df.groupby("black_algorithm")["win_rate"].mean()
        win_rates.plot(kind="bar", color=["skyblue", "lightgreen"])
        plt.title("Win Rate by Algorithm (as Black)")
        plt.ylabel("Win Rate")
        plt.xticks(rotation=0)
        plt.tight_layout()

        plot_path = os.path.join(os.getcwd(), "algorithm_win_rates.png")
        print(f"Saving algorithm win rate plot to: {plot_path}")
        plt.savefig(plot_path)
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

        time_plot_path = os.path.join(os.getcwd(), "algorithm_times.png")
        print(f"Saving algorithm time plot to: {time_plot_path}")
        plt.savefig(time_plot_path)
        plt.close()
        print("Algorithm plots generated successfully")

    except Exception as e:
        print(f"Error generating algorithm plots: {str(e)}")
        import traceback

        traceback.print_exc()


def check_othello_command():
    """Check if the othello command is available"""
    try:
        print("Checking if othello command is available...")
        result = subprocess.run(["othello", "--help"], capture_output=True, text=True)
        if result.returncode == 0:
            print("Othello command is available!")
            return True
        else:
            print(f"Othello command returned non-zero exit code: {result.returncode}")
            print(f"Error output: {result.stderr}")
            return False
    except FileNotFoundError:
        print("Othello command not found! Make sure it's installed and in your PATH.")
        return False
    except Exception as e:
        print(f"Error checking othello command: {str(e)}")
        return False


if __name__ == "__main__":
    print(f"Script running in directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")

    if not check_othello_command():
        print(
            "Othello command not available. Please make sure it's installed and in your PATH."
        )
        print(
            "You might need to provide the full path to the othello executable in the script."
        )
        sys.exit(1)

    try:
        print("Starting heuristic benchmark...")
        run_heuristic_benchmark()
        print("Heuristic benchmark complete. Starting algorithm benchmark...")
        run_algorithm_benchmark()
        print("All benchmarks complete!")

        # List files in current directory to check if CSVs were created
        print("\nFiles in current directory:")
        for file in os.listdir(os.getcwd()):
            print(f"  {file}")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        import traceback

        traceback.print_exc()
