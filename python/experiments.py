import numpy as np
import matplotlib.pyplot as plt
import time
from multiprocessing import cpu_count
from simulation.sequential import run_sequential
from simulation.parallel import step_parallel
from simulation.const import *
from numba import set_num_threads, get_num_threads

def amdahl_speedup(p, n):
    return 1 / ((1 - p) + p / n)

def gustafson_speedup(p, n):
    return n - (1 - p) * (n - 1)

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
        
        if parallel and n_workers is not None:
            set_num_threads(n_workers)

        start = time.time()
        for _ in range(steps):
            if parallel:
                g = step_parallel(g)
            else:
                g = run_sequential(g, 1)
        times.append(time.time() - start)
    mean_time = np.mean(times)
    std_time = np.std(times)
    return mean_time, std_time

def strong_scaling_experiment(width, height, steps=10, p=0.95):
    max_workers = cpu_count()
    grid = initialize_forest(width, height)
    seq_time, seq_std = measure_time(grid, steps, parallel=False)

    results = []
    for workers in range(1, max_workers + 1):
        par_time, std = measure_time(grid, steps, parallel=True, n_workers=workers)
        speedup = seq_time / par_time
        ideal = amdahl_speedup(p, workers)
        results.append({
            "workers": workers,
            "time": par_time,
            "std": std,
            "speedup": speedup,
            "ideal": ideal
        })
    return results, seq_time

def weak_scaling_experiment(base_width, base_height, steps=10):
    max_workers = cpu_count()

    set_num_threads(1)
    base_grid = initialize_forest(base_width, base_height)
    base_time, _ = measure_time(base_grid, steps, parallel=True, n_workers=1)

    results = []

    for workers in range(1, max_workers + 1):
        set_num_threads(workers)

        width = base_width * workers
        height = base_height

        grid = initialize_forest(width, height)

        par_time, std = measure_time(grid, steps, parallel=True, n_workers=workers)

        results.append({
            "workers": workers,
            "time": par_time,
            "std": std,
            "baseline": base_time
        })

    return results

def plot_strong(results, title="Python Strong Scaling (Time)"):
    workers = [r["workers"] for r in results]
    times = [r["time"] for r in results]

    plt.figure()
    plt.plot(workers, times, "o-", label="Observed time")

    plt.xlabel("Number of cores")
    plt.ylabel("Execution time (s)")
    plt.title(title)
    plt.legend()
    plt.grid(True)

    plt.show()

def plot_weak(results, title="Python Weak Scaling"):
    workers = [r["workers"] for r in results]
    times = [r["time"] for r in results]
    baseline = results[0]["baseline"]

    plt.figure()
    plt.plot(workers, times, "o-", label="Observed time")
    plt.axhline(baseline, linestyle="--", label="Ideal (constant time)")
    plt.xlabel("Number of cores")
    plt.ylabel("Execution time (s)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

def strong_scaling_table(width, height, steps=300, runs=30, workers_list=[1,2,4]):
    grid = initialize_forest(width, height)

    serial_times = []
    for _ in range(runs):
        t, _ = measure_time(grid, steps, parallel=False)
        serial_times.append(t)

    table = []

    for i in range(runs):
        row = {"run": i+1, "serial": serial_times[i]}

        for w in workers_list:
            t, _ = measure_time(grid, steps, parallel=True, n_workers=w)
            row[f"{w}T"] = t

        table.append(row)

    return table

def weak_scaling_table(base_width, base_height, steps=300, runs=30, workers_list=[1,2,4]):
    table = []

    for i in range(runs):
        row = {"run": i+1}

        for w in workers_list:
            width = base_width * w
            height = base_height

            grid = initialize_forest(width, height)
            t, _ = measure_time(grid, steps, parallel=True, n_workers=w)
            row[f"{w}T"] = t

        table.append(row)

    return table


def print_table(table, workers_list=[1,2,4]):
    header = "Run | Serial | " + " | ".join(f"{w}T" for w in workers_list)
    print(header)
    print("-" * len(header))

    for r in table:
        line = f"{r['run']:>3} | {r['serial']:.3f} | " + " | ".join(
            f"{r[f'{w}T']:.3f}" for w in workers_list
        )
        print(line)

def plot_speedup(table, workers_list=[1,2,4], p=0.95):

    serial_mean = np.mean([r["serial"] for r in table])

    observed = []
    for w in workers_list:
        par_mean = np.mean([r[f"{w}T"] for r in table])
        observed.append(serial_mean / par_mean)

    amdahl = [amdahl_speedup(p, w) for w in workers_list]
    gustafson = [gustafson_speedup(p, w) for w in workers_list]

    plt.figure()
    plt.plot(workers_list, observed, "o-", label="Observed")
    plt.plot(workers_list, amdahl, "--", label="Amdahl ideal")
    plt.plot(workers_list, gustafson, ":", label="Gustafson ideal")

    plt.xlabel("Workers")
    plt.ylabel("Speedup")
    plt.title("Strong Scaling Speedup")
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_weak_efficiency(table, workers_list=[1,2,4]):
    base_mean = np.mean([r["1T"] for r in table])

    efficiency = []
    for w in workers_list:
        mean_t = np.mean([r[f"{w}T"] for r in table])
        efficiency.append(base_mean / mean_t)

    plt.figure()
    plt.plot(workers_list, efficiency, "o-", label="Observed")
    plt.axhline(1.0, linestyle="--", label="Ideal")

    plt.xlabel("Workers")
    plt.ylabel("Efficiency")
    plt.title("Weak Scaling")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    width, height = 1024, 1024
    steps = 300

    print("\n=== STRONG SCALING===")
    strong_table = strong_scaling_table(width, height, steps)
    print_table(strong_table)

    plot_speedup(strong_table)

    print("\n=== WEAK SCALING ===")
    weak_table = weak_scaling_table(width, height, steps)

    for r in weak_table[:5]:
        print(r)

    plot_weak_efficiency(weak_table)
