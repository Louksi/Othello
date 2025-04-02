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


def plot_interactive_comparison(df):
    """Interactive 3D plot using Plotly"""
    fig = px.scatter_3d(
        df,
        x="ai_depth",
        y="avg_time",
        z="speedup_factor",
        color="ai_heuristic",
        symbol="ai_mode",
        size="avg_moves_per_run",
        hover_name="ai_heuristic",
        title="AI Performance Characteristics",
        labels={
            "ai_depth": "Search Depth",
            "avg_time": "Avg Time (s)",
            "speedup_factor": "Speedup Factor",
            "ai_heuristic": "Heuristic",
        },
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Search Depth",
            yaxis_title="Time (seconds)",
            zaxis_title="Speedup vs Baseline",
        ),
        margin=dict(l=0, r=0, b=0, t=30),
    )

    fig.write_html("interactive_3d_plot.html")
    fig.show()


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


def main():
    # Load all results
    df = load_and_combine_results()

    # Convert to numeric where needed
    numeric_cols = ["avg_time", "baseline_time", "speedup_factor", "avg_moves_per_run"]
    df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)

    # Generate visualizations
    plot_time_comparison(df)
    plot_speedup_heatmap(df)
    plot_heuristic_comparison(df)
    plot_interactive_comparison(df)

    # Save combined data
    df.to_csv("combined_results.csv", index=False)
    print("Visualizations saved and data combined to 'combined_results.csv'")


if __name__ == "__main__":
    main()
