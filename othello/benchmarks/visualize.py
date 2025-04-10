import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from othello.parser import AIHeuristic


def create_experiment1_visualizations(csv_path="experiment1_results.csv"):
    """
    Create simple bar graphs comparing only winrate and speed of alpha-beta vs minimax
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import seaborn as sns
        import numpy as np
    except ImportError:
        print(
            "Visualization libraries not available. Install pandas, matplotlib, and seaborn to generate plots."
        )
        return

    # Load data
    df = pd.read_csv(csv_path)

    # Calculate average execution times by algorithm
    minimax_times = []
    minimax_times.extend(
        df[df["black_ai_mode"] == "minimax"]["avg_black_execution_time"].tolist()
    )
    minimax_times.extend(
        df[df["white_ai_mode"] == "minimax"]["avg_white_execution_time"].tolist()
    )

    ab_times = []
    ab_times.extend(
        df[df["black_ai_mode"] == "ab"]["avg_black_execution_time"].tolist()
    )
    ab_times.extend(
        df[df["white_ai_mode"] == "ab"]["avg_white_execution_time"].tolist()
    )

    # Calculate the average time for each algorithm
    avg_minimax_time = np.mean(minimax_times)
    avg_ab_time = np.mean(ab_times)

    # Create the bar graph
    plt.figure(figsize=(10, 6))

    algorithms = ["Minimax", "Alpha-Beta"]
    avg_times = [avg_minimax_time, avg_ab_time]

    # Create the bar plot
    sns.barplot(x=algorithms, y=avg_times)

    # Add labels and title
    plt.xlabel("Algorithm")
    plt.ylabel("Average Execution Time (seconds)")
    plt.title("Average Execution Time Comparison: Minimax vs Alpha-Beta at depth 8")

    # Add the actual values on top of each bar
    for i, v in enumerate(avg_times):
        plt.text(i, v + 0.01, f"{v:.4f}s", ha="center")

    # Save the plot if needed
    plt.tight_layout()
    plt.savefig("algorithm_time_comparison.png")
    plt.show()


def line_graph_depth(csv_path="experiment4_results.csv"):
    df = pd.read_csv(csv_path)
    results = []
    results.extend(df[df["black_ai_mode"] == "ab"]["avg_black_execution_time"].tolist())
    plt.figure(figsize=(10, 6))
    for heuristic in AIHeuristic:
        depths_tested = list(results[heuristic].keys())
        times = [results[heuristic][d] for d in depths_tested]
        plt.plot(depths_tested, times, label=heuristic, marker="o")

    plt.title("Alpha-Beta Time by Depth")
    plt.xlabel("Depth")
    plt.ylabel("Time (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig("alpha_beta_time_by_depth.png")
    plt.show()


def plot_exp4(results, filename="alpha_beta_time_by_depth.png"):
    """
    Plot the Alpha-Beta time by depth for different heuristics

    Args:
        results: Dictionary in format {heuristic: {depth: avg_time}}
        filename: Where to save the plot image
    """
    plt.figure(figsize=(10, 6))

    # Define colors/markers for each heuristic for consistent plotting
    styles = {
        "corners_captured": {"color": "blue", "marker": "o"},
        "coin_parity": {"color": "green", "marker": "s"},
        "mobility": {"color": "red", "marker": "^"},
        "all_in_one": {"color": "purple", "marker": "D"},
    }

    for heuristic in results:
        depths = sorted(results[heuristic].keys())
        times = [results[heuristic][d] for d in depths]

        plt.plot(
            depths,
            times,
            label=heuristic,
            marker=styles[heuristic]["marker"],
            color=styles[heuristic]["color"],
            linestyle="-",
            linewidth=2,
            markersize=8,
        )

    plt.title("Alpha-Beta Time by Depth", fontsize=14)
    plt.xlabel("Depth", fontsize=12)
    plt.ylabel("Time (seconds)", fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.7)

    # Adjust x-axis to show integer depths only
    plt.xticks(range(1, 11))

    # Save and show
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()


if __name__ == "__main__":
    create_experiment1_visualizations()
    print("Visualization complete!")
