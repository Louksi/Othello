import subprocess

experiments = [
    "expermiment_minimax_vs_ab.py",
]

for exp in experiments:
    print(f"\n{'='*50}")
    print(f"Running {exp}")
    print(f"{'='*50}")
    subprocess.run(["python", exp])
