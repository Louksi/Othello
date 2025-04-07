import subprocess
import re
import time
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from enum import Enum
from itertools import product
from concurrent.futures import ProcessPoolExecutor
import os


class AIMode(Enum):
    MINIMAX = "minimax"
    ALPHABETA = "ab"


class AIHeuristic(Enum):
    CORNERS_CAPTURED = "corners_captured"
    COIN_PARITY = "coin_parity"
    MOBILITY = "mobility"
    STABILITY = "stability"
    ALL_IN_ONE = "all_in_one"


# Patterns to extract game information
time_pattern = re.compile(r"Time taken: (\d+\.\d+) seconds")
score_pattern = re.compile(r"Final score: X:(\d+), O:(\d+)")
move_pattern = re.compile(r"Total moves: (\d+)")
nodes_pattern = re.compile(
    r"Nodes evaluated: (\d+)"
)  # Add this if your Othello program outputs nodes evaluated


def run_single_game(config):
    """Run a single game with the given configuration"""
    black_config = config["black_config"]
    white_config = config["white_config"]
    board_size = config["board_size"]
    game_id = config["game_id"]

    # Create command for the game
    cmd = [
        "othello",
        "--benchmark",  # Run in benchmark mode
        "-a",
        "B",  # Both players are AI
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
        # Run the game process
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True)
        total_time = time.time() - start_time
        output = result.stdout

        # Parse final board state to get score
        # Look for the last board state in the output
        board_states = re.findall(
            r"(  a b c d e f g h\n.*?BLACK|WHITE)", output, re.DOTALL
        )

        if not board_states:
            print(f"Could not find board state in game {game_id}")
            return None

        last_board = board_states[-1]

        # Count X and O pieces on the board
        black_score = last_board.count("X")
        white_score = last_board.count("O")

        # Parse move count - find the last turn number
        turn_matches = re.findall(r"=== turn (\d+) ===", output)
        total_moves = int(turn_matches[-1]) if turn_matches else 0

        # Calculate time per player - this will be approximate since we don't have per-move timing
        # For a more accurate approach, you would need to modify your Othello program to output timing information
        # For now, we'll assume equal distribution
        avg_time_per_move = total_time / (total_moves * 2) if total_moves > 0 else 0

        # Determine winner
        if black_score > white_score:
            winner = "black"
        elif white_score > black_score:
            winner = "white"
        else:
            winner = "draw"

        return {
            "black_heuristic": black_config["heuristic"].value,
            "black_depth": black_config["depth"],
            "white_heuristic": white_config["heuristic"].value,
            "white_depth": white_config["depth"],
            "black_score": black_score,
            "white_score": white_score,
            "winner": winner,
            "avg_time_per_move": avg_time_per_move,
            "total_time": total_time,
            "total_moves": total_moves,
            "game_id": game_id,
        }
    except Exception as e:
        print(f"Error running game {game_id}: {e}")
        return None


def run_depth_analysis(baseline_depth=2, max_depth=8, step=1, num_games=5):
    """
    Run depth analysis for each heuristic using alpha-beta pruning.

    Parameters:
    - baseline_depth: The depth to use for the baseline (white player)
    - max_depth: Maximum depth to test for black player
    - step: Step size for depth increments
    - num_games: Number of games to run for each configuration
    """
    board_size = 8
    mode = AIMode.ALPHABETA
    heuristics = list(AIHeuristic)

    depths = list(range(baseline_depth, max_depth + 1, step))
    results = []

    # Set up configurations for parallel execution
    configs = []
    game_counter = 0

    # Create baseline AI config with fixed depth
    baseline_config = {
        "mode": mode,
        "depth": baseline_depth,
        "heuristic": AIHeuristic.ALL_IN_ONE,  # Using the combined heuristic as baseline
    }

    # Test each heuristic with increasing depths against baseline
    for heuristic in heuristics:
        for depth in depths:
            for game in range(num_games):
                test_config = {"mode": mode, "depth": depth, "heuristic": heuristic}

                # Test as black vs baseline
                configs.append(
                    {
                        "black_config": test_config,
                        "white_config": baseline_config,
                        "board_size": board_size,
                        "game_id": game_counter,
                    }
                )
                game_counter += 1

                # Test as white vs baseline
                configs.append(
                    {
                        "black_config": baseline_config,
                        "white_config": test_config,
                        "board_size": board_size,
                        "game_id": game_counter,
                    }
                )
                game_counter += 1

    total_games = len(configs)
    print(f"Running {total_games} games for depth analysis...")

    # Use parallel execution to speed up the process
    max_workers = os.cpu_count() or 4
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Map configurations to the executor
        for i, result in enumerate(executor.map(run_single_game, configs)):
            if result:
                results.append(result)

            # Print progress
            if (i + 1) % 10 == 0 or i + 1 == total_games:
                print(
                    f"Progress: {i+1}/{total_games} games completed ({(i+1)/total_games*100:.1f}%)"
                )

    # Save results to CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv("depth_analysis_results.csv", index=False)

    # Generate visualizations
    plot_depth_analysis_results(results_df, depths, heuristics)

    return results_df


def plot_depth_analysis_results(df, depths, heuristics):
    """Create visualizations from depth analysis results"""

    # Preprocess data for plotting
    # Calculate win rates for each depth and heuristic
    win_rates = {}
    for heuristic in [h.value for h in heuristics]:
        win_rates[heuristic] = []
        for depth in depths:
            # Get games where this heuristic played as black at this depth
            black_games = df[
                (df["black_heuristic"] == heuristic) & (df["black_depth"] == depth)
            ]
            wins = len(black_games[black_games["winner"] == "black"])
            total = len(black_games)
            win_rate = wins / total if total > 0 else 0
            win_rates[heuristic].append(win_rate)

    # 1. Win rate by depth for each heuristic
    plt.figure(figsize=(12, 8))
    for heuristic in win_rates:
        plt.plot(depths, win_rates[heuristic], marker="o", label=heuristic)

    plt.title("Win Rate vs. Search Depth by Heuristic")
    plt.xlabel("Search Depth")
    plt.ylabel("Win Rate")
    plt.xticks(depths)
    plt.ylim(0, 1)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig("depth_win_rates.png")
    plt.close()

    # 2. Execution time by depth for each heuristic
    plt.figure(figsize=(12, 8))

    for heuristic in [h.value for h in heuristics]:
        avg_times = []
        for depth in depths:
            heuristic_depth_games = df[
                (df["black_heuristic"] == heuristic) & (df["black_depth"] == depth)
            ]
            avg_time = heuristic_depth_games["black_avg_time"].mean()
            avg_times.append(avg_time)

        plt.plot(depths, avg_times, marker="o", label=heuristic)

    plt.title("Average Move Time vs. Search Depth by Heuristic")
    plt.xlabel("Search Depth")
    plt.ylabel("Average Move Time (seconds)")
    plt.xticks(depths)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig("depth_execution_times.png")
    plt.close()

    # 3. Score difference by depth
    plt.figure(figsize=(12, 8))

    for heuristic in [h.value for h in heuristics]:
        avg_score_diffs = []
        for depth in depths:
            heuristic_depth_games = df[
                (df["black_heuristic"] == heuristic) & (df["black_depth"] == depth)
            ]
            avg_score_diff = (
                heuristic_depth_games["black_score"]
                - heuristic_depth_games["white_score"]
            ).mean()
            avg_score_diffs.append(avg_score_diff)

        plt.plot(depths, avg_score_diffs, marker="o", label=heuristic)

    plt.title("Average Score Difference vs. Search Depth by Heuristic")
    plt.xlabel("Search Depth")
    plt.ylabel("Average Score Difference (Black - White)")
    plt.xticks(depths)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.axhline(y=0, color="k", linestyle="-", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("depth_score_differences.png")
    plt.close()

    # 4. Performance efficiency (win rate / time)
    plt.figure(figsize=(12, 8))

    for heuristic in [h.value for h in heuristics]:
        efficiency = []
        for depth in depths:
            heuristic_depth_games = df[
                (df["black_heuristic"] == heuristic) & (df["black_depth"] == depth)
            ]
            wins = len(
                heuristic_depth_games[heuristic_depth_games["winner"] == "black"]
            )
            total = len(heuristic_depth_games)
            win_rate = wins / total if total > 0 else 0
            avg_time = heuristic_depth_games["black_avg_time"].mean()
            eff = win_rate / avg_time if avg_time > 0 else 0
            efficiency.append(eff)

        plt.plot(depths, efficiency, marker="o", label=heuristic)

    plt.title("Performance Efficiency (Win Rate / Time) by Depth and Heuristic")
    plt.xlabel("Search Depth")
    plt.ylabel("Efficiency (Win Rate / Average Time)")
    plt.xticks(depths)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.tight_layout()
    plt.savefig("depth_efficiency.png")
    plt.close()

    # 5. Heatmap showing win rate across depths and heuristics
    pivot_data = []
    for heuristic in [h.value for h in heuristics]:
        for depth in depths:
            black_games = df[
                (df["black_heuristic"] == heuristic) & (df["black_depth"] == depth)
            ]
            wins = len(black_games[black_games["winner"] == "black"])
            total = len(black_games)
            win_rate = wins / total if total > 0 else 0
            pivot_data.append(
                {"Heuristic": heuristic, "Depth": depth, "Win Rate": win_rate}
            )

    pivot_df = pd.DataFrame(pivot_data)
    pivot_table = pivot_df.pivot(index="Heuristic", columns="Depth", values="Win Rate")

    plt.figure(figsize=(12, 8))
    sns.heatmap(
        pivot_table,
        annot=True,
        cmap="YlGnBu",
        vmin=0,
        vmax=1,
        cbar_kws={"label": "Win Rate"},
    )
    plt.title("Win Rate by Heuristic and Depth")
    plt.tight_layout()
    plt.savefig("depth_heuristic_heatmap.png")
    plt.close()

    # 6. If nodes evaluated data is available, plot that too
    if "black_nodes" in df.columns and not df["black_nodes"].isna().all():
        plt.figure(figsize=(12, 8))

        for heuristic in [h.value for h in heuristics]:
            avg_nodes = []
            for depth in depths:
                heuristic_depth_games = df[
                    (df["black_heuristic"] == heuristic) & (df["black_depth"] == depth)
                ]
                avg_node_count = heuristic_depth_games["black_nodes"].mean()
                avg_nodes.append(avg_node_count)

            plt.plot(depths, avg_nodes, marker="o", label=heuristic)

        plt.title("Average Nodes Evaluated vs. Search Depth by Heuristic")
        plt.xlabel("Search Depth")
        plt.ylabel("Average Nodes Evaluated")
        plt.xticks(depths)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend()
        plt.tight_layout()
        plt.savefig("depth_nodes_evaluated.png")
        plt.close()


def optimize_depth_for_time_constraint(results_df, time_limit=1.0):
    """Determine optimal depth for each heuristic given a time constraint"""
    optimal_depths = {}

    for heuristic in results_df["black_heuristic"].unique():
        heuristic_df = results_df[results_df["black_heuristic"] == heuristic]

        # Group by depth and calculate average time
        depth_times = heuristic_df.groupby("black_depth")["black_avg_time"].mean()

        # Find deepest depth that meets time constraint
        valid_depths = depth_times[depth_times <= time_limit]
        if not valid_depths.empty:
            optimal_depth = valid_depths.index.max()

            # Get win rate at this depth
            depth_games = heuristic_df[heuristic_df["black_depth"] == optimal_depth]
            wins = len(depth_games[depth_games["winner"] == "black"])
            total = len(depth_games)
            win_rate = wins / total if total > 0 else 0

            optimal_depths[heuristic] = {
                "optimal_depth": optimal_depth,
                "avg_time": depth_times[optimal_depth],
                "win_rate": win_rate,
            }
        else:
            # If no depth meets constraint, use minimum depth
            min_depth = depth_times.index.min()
            depth_games = heuristic_df[heuristic_df["black_depth"] == min_depth]
            wins = len(depth_games[depth_games["winner"] == "black"])
            total = len(depth_games)
            win_rate = wins / total if total > 0 else 0

            optimal_depths[heuristic] = {
                "optimal_depth": min_depth,
                "avg_time": depth_times[min_depth],
                "win_rate": win_rate,
                "note": "Exceeds time constraint",
            }

    # Create summary table
    summary_df = pd.DataFrame.from_dict(optimal_depths, orient="index")
    summary_df.reset_index(inplace=True)
    summary_df.rename(columns={"index": "heuristic"}, inplace=True)

    # Save to CSV
    summary_df.to_csv(f"optimal_depths_for_{time_limit}s.csv", index=False)

    return optimal_depths


if __name__ == "__main__":
    # Configure parameters
    baseline_depth = 2
    max_depth = 8
    step = 1
    num_games = 5  # Increase for more reliable results

    print(f"Running depth analysis from depth {baseline_depth} to {max_depth}...")
    results = run_depth_analysis(baseline_depth, max_depth, step, num_games)

    # Find optimal depths for different time constraints
    print("Finding optimal depths for different time constraints...")
    optimize_depth_for_time_constraint(results, time_limit=0.5)  # Fast-paced game
    optimize_depth_for_time_constraint(results, time_limit=1.0)  # Standard
    optimize_depth_for_time_constraint(results, time_limit=2.0)  # Deep analysis

    print(
        "Depth analysis complete! Results saved to CSV files and visualizations saved as PNG files."
    )
