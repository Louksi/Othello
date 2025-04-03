import subprocess

experiments = [
    "benchmark_winrates.py",
]

for exp in experiments:
    print(f"\n{'='*50}")
    print(f"Running {exp}")
    print(f"{'='*50}")
    subprocess.run(["python", exp])
