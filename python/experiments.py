# experiments.py
import numpy as np
import matplotlib.pyplot as plt
from simulation.sequential import run_sequential
from simulation.parallel import step_parallel
from simulation.const import *
import time
from multiprocessing import cpu_count

def initialize_forest(width, height, thick_ratio=0.15):
    grid = np.random.choice(
        [EMPTY, TREE],
        size=(height, width),
        p=[0.2, 0.8]
    )
    tree_cells = np.where(grid == TREE)
    num_thick = int(len(tree_cells[0]) * thick_ratio)
    if num_thick > 0:
        indices = np.random.choice(len(tree_cells[0]), num_thick, replace=False)
        grid[tree_cells[0][indices], tree_cells[1][indices]] = THICK_TREE
    return grid

def measure_time(grid, steps=10, parallel=False, n_workers=None):
    times = []
    for _ in range(5):
        g = grid.copy()
        start = time.time()
        for _ in range(steps):
            if parallel:
                g = step_parallel(g, n_workers)
            else:
                g = run_sequential(g, 1)
        end = time.time()
        times.append(end - start)
    mean_time = np.mean(times)
    std_time = np.std(times)
    return mean_time, std_time

def strong_scaling_experiment(width, height, steps=10):
    max_workers = cpu_count()
    grid = initialize_forest(width, height)
    seq_time, _ = measure_time(grid, steps, parallel=False)
    results = []
    for workers in range(1, max_workers + 1):
        par_time, std = measure_time(grid, steps, parallel=True, n_workers=workers)
        speedup = seq_time / par_time
        results.append((workers, speedup, par_time, std))
    return results, seq_time

def weak_scaling_experiment(base_width, base_height, steps=10):
    max_workers = cpu_count()
    results = []
    for workers in range(1, max_workers + 1):
        width = base_width * workers
        height = base_height * workers
        grid = initialize_forest(width, height)
        par_time, std = measure_time(grid, steps, parallel=True, n_workers=workers)
        results.append((workers, par_time, std))
    return results

def plot_speedup(results, seq_time=None, title="Strong Scaling"):
    workers = [r[0] for r in results]
    speedup = [r[1] for r in results]
    plt.figure()
    plt.plot(workers, speedup, "o-", label="Observed speedup")
    if seq_time is not None:
        plt.plot(workers, workers, "--", label="Ideal speedup")
    plt.xlabel("Number of cores")
    plt.ylabel("Speedup")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_times(results, title="Weak Scaling"):
    workers = [r[0] for r in results]
    times = [r[1] for r in results]
    plt.figure()
    plt.plot(workers, times, "o-", label="Observed time")
    plt.xlabel("Number of cores")
    plt.ylabel("Execution time (s)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    width, height = 256, 256
    steps = 10

    print("Strong scaling")
    strong_results, seq_time = strong_scaling_experiment(width, height, steps)
    plot_speedup(strong_results, seq_time, title="Python Strong Scaling")

    print("Weak scaling")
    weak_results = weak_scaling_experiment(width, height, steps)
    plot_times(weak_results, title="Python Weak Scaling")
