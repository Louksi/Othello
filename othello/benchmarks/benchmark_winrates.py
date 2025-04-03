import itertools
import subprocess
import re
from enum import Enum
import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
from benchmarks_utils import AIMode, AIHeuristic


class Player(Enum):
    BLACK = "black"
    WHITE = "white"
    DRAW = "draw"


# Configuration parameters
board_sizes = [6]
ai_depths = [2]
ai_modes = [AIMode.MINIMAX, AIMode.ALPHABETA]
ai_heuristics = [
    AIHeuristic.CORNERS_CAPTURED,
    AIHeuristic.COIN_PARITY,
    AIHeuristic.MOBILITY,
    AIHeuristic.ALL_IN_ONE,
]
num_games = 10  # Number of games per configuration

# Result patterns
result_pattern = re.compile(r"Final score - Black: (\d+), White: (\d+)")
move_pattern = re.compile(r"placed a piece at ([A-H]\d+)")


def run_game(size, depth, mode, heuristic, game_num):
    """Run a single game and return the winner"""
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

        # Parse winner
        match = result_pattern.search(output)
        if match:
            black_score = int(match.group(1))
            white_score = int(match.group(2))

            if black_score > white_score:
                return Player.BLACK, black_score - white_score
            elif white_score > black_score:
                return Player.WHITE, white_score - black_score
            else:
                return Player.DRAW, 0

        # Count moves if needed
        moves = move_pattern.findall(output)
        return None, len(moves)

    except Exception as e:
        print(f"Error running game: {e}")
        return None, 0


def benchmark_winrates():
    results = []

    for size, depth, mode, heuristic in itertools.product(
        board_sizes, ai_depths, ai_modes, ai_heuristics
    ):
        print(
            f"\nBenchmarking: size={size}, depth={depth}, mode={mode.value}, heuristic={heuristic.value}"
        )

        wins = defaultdict(int)
        total_margin = 0
        move_counts = []

        for game in range(num_games):
            winner, margin = run_game(size, depth, mode, heuristic, game + 1)
            if winner:
                wins[winner] += 1
                total_margin += margin

                # Store move count if available
                if (
                    isinstance(margin, int) and margin > 0
                ):  # Actually move count comes separately
                    move_counts.append(margin)

            print(f"  Game {game+1}: {winner.value if winner else 'error'}", end="\r")

        if wins:
            results.append(
                {
                    "board_size": size,
                    "ai_depth": depth,
                    "ai_mode": mode.value,
                    "ai_heuristic": heuristic.value,
                    "games_played": num_games,
                    "black_wins": wins[Player.BLACK],
                    "white_wins": wins[Player.WHITE],
                    "draws": wins[Player.DRAW],
                    "win_rate": (wins[Player.BLACK] + 0.5 * wins[Player.DRAW])
                    / num_games,
                    "avg_margin": (
                        total_margin / (wins[Player.BLACK] + wins[Player.WHITE])
                        if (wins[Player.BLACK] + wins[Player.WHITE]) > 0
                        else 0
                    ),
                    "avg_moves": (
                        sum(move_counts) / len(move_counts) if move_counts else 0
                    ),
                }
            )

    # Save results
    df = pd.DataFrame(results)
    df.to_csv("winrate_results.csv", index=False)
    return df


if __name__ == "__main__":
    benchmark_winrates()
