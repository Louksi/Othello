import subprocess

experiments = [
    "experiment_baseline.py",
    "experiment_heuristics.py",
    "experiment_minimax_vs_ab.py",
]

for exp in experiments:
    print(f"\n{'='*50}")
    print(f"Running {exp}")
    print(f"{'='*50}")
    subprocess.run(["python", exp])
