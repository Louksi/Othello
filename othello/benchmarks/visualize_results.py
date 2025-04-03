import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from pathlib import Path

# Set style for better looking plots
sns.set(style="whitegrid")
plt.style.use("seaborn-v0_8-poster")


def load_and_combine_results():
    """Load all result files into one DataFrame"""
    result_files = ["minimax_vs_ab_results.csv", "heuristics_results.csv"]

    dfs = []
    for f in result_files:
        if Path(f).exists():
            df = pd.read_csv(f)
            dfs.append(df)

    if not dfs:
        raise FileNotFoundError("No result files found. Run experiments first.")

    return pd.concat(dfs, ignore_index=True)


def plot_time_comparison(df):
    """Compare performance across different configurations"""
    plt.figure(figsize=(14, 8))

    # Create a combined label for x-axis
    df["config"] = df.apply(
        lambda row: f"{row['ai_mode']} d{row['ai_depth']} {row['ai_heuristic']}", axis=1
    )

    # Plot grouped bars
    sns.barplot(data=df, x="config", y="avg_time", hue="board_size", palette="viridis")

    plt.title("Average Move Time by Configuration")
    plt.ylabel("Time (seconds)")
    plt.xlabel("AI Configuration")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Board Size")
    plt.tight_layout()
    plt.savefig("time_comparison.png", dpi=300)
    plt.show()


def plot_speedup_heatmap(df):
    """Heatmap of speedup factors"""
    plt.figure(figsize=(12, 8))

    # Pivot for heatmap
    heatmap_data = df.pivot_table(
        index=["ai_mode", "ai_depth"],
        columns=["ai_heuristic", "board_size"],
        values="speedup_factor",
    )

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".1f",
        cmap="YlGnBu",
        linewidths=0.5,
        cbar_kws={"label": "Speedup Factor (vs baseline)"},
    )

    plt.title("Performance Speedup Factors")
    plt.tight_layout()
    plt.savefig("speedup_heatmap.png", dpi=300)
    plt.show()


def plot_heuristic_comparison(df):
    """Compare heuristics at max depth"""
    max_depth = df["ai_depth"].max()
    deep_df = df[df["ai_depth"] == max_depth]

    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=deep_df,
        x="ai_heuristic",
        y="speedup_factor",
        hue="board_size",
        palette="rocket",
    )

    plt.title(f"Performance of Heuristics at Depth {max_depth}")
    plt.ylabel("Speedup Factor (vs baseline)")
    plt.xlabel("Heuristic")
    plt.xticks(rotation=15)
    plt.legend(title="Board Size")
    plt.tight_layout()
    plt.savefig("heuristic_comparison.png", dpi=300)
    plt.show()


# Add these new functions to your existing visualization script


def plot_winrate_comparison(df):
    """Compare win rates across configurations"""
    plt.figure(figsize=(14, 8))

    # Create combined label
    df["config"] = df.apply(
        lambda row: f"{row['ai_mode']} d{row['ai_depth']} {row['ai_heuristic']}", axis=1
    )

    # Plot win rates
    sns.barplot(data=df, x="config", y="win_rate", hue="board_size", palette="coolwarm")

    plt.title("AI Win Rate by Configuration")
    plt.ylabel("Win Rate")
    plt.xlabel("AI Configuration")
    plt.xticks(rotation=45, ha="right")
    plt.ylim(0, 1)
    plt.legend(title="Board Size")
    plt.tight_layout()
    plt.savefig("winrate_comparison.png", dpi=300)
    plt.show()


def plot_win_loss_distribution(df):
    """Show win/loss/draw distribution"""
    plt.figure(figsize=(12, 6))

    # Melt the data for stacked bar plot
    melt_df = df.melt(
        id_vars=["config", "board_size"],
        value_vars=["black_wins", "white_wins", "draws"],
        var_name="result",
        value_name="count",
    )

    sns.barplot(
        data=melt_df,
        x="config",
        y="count",
        hue="result",
        palette={"black_wins": "black", "white_wins": "lightgray", "draws": "red"},
    )

    plt.title("Win/Loss/Draw Distribution")
    plt.ylabel("Number of Games")
    plt.xlabel("AI Configuration")
    plt.xticks(rotation=45, ha="right")
    plt.legend(title="Result")
    plt.tight_layout()
    plt.savefig("win_loss_distribution.png", dpi=300)
    plt.show()


# Update your main function to include win rate visualizations
def main():
    # Load all results
    time_df = load_and_combine_results()  # Your existing time benchmarks
    winrate_df = pd.read_csv("winrate_results.csv")  # New win rate data

    # Generate visualizations
    plot_time_comparison(time_df)
    plot_speedup_heatmap(time_df)
    plot_heuristic_comparison(time_df)

    # New win rate visualizations
    plot_winrate_comparison(winrate_df)
    plot_win_loss_distribution(winrate_df)

    # Save combined data
    combined_df = pd.merge(
        time_df,
        winrate_df,
        on=["board_size", "ai_depth", "ai_mode", "ai_heuristic"],
        how="outer",
    )
    combined_df.to_csv("combined_results.csv", index=False)


if __name__ == "__main__":
    main()
