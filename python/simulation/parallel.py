import numpy as np
from threading import Thread
from simulation.const import *
from multiprocessing import cpu_count
def _worker(grid, new_grid, start, end):
    chunk = grid[start:end]
    burning = (chunk == BURNING)
    tree = (chunk == TREE)
    empty = (chunk == EMPTY)

    padded_burning = np.pad(burning, pad_width=1, mode='constant', constant_values=False)

    fire_risk_tree = np.zeros_like(chunk, dtype=bool)
    for dy in [0, 1, 2]:
        for dx in [0, 1, 2]:
            if dy == 1 and dx == 1:
                continue
            fire_risk_tree |= padded_burning[dy:dy + chunk.shape[0], dx:dx + chunk.shape[1]]&(
                np.random.rand(*chunk.shape) < FIRE_SPREAD_CHANCE)

    new_chunk = chunk.copy()
    new_chunk[burning] = EMPTY
    new_chunk[tree & fire_risk_tree] = BURNING
    new_chunk[tree & (np.random.rand(*chunk.shape) < LIGHTNING_CHANCE)] = BURNING
    new_chunk[empty & (np.random.rand(*chunk.shape) < GROWTH_CHANCE)] = TREE

    new_grid[start:end] = new_chunk


def step_parallel(grid, n_threads=None):    
    n_threads = cpu_count()

    h, _ = grid.shape
    chunk_h = h // n_threads
    threads = []
    new_grid = np.empty_like(grid)

    for i in range(n_threads):
        start = max(i * chunk_h - 1, 0)
        end = min((i + 1) * chunk_h + 1, h)
        t = Thread(target=_worker, args=(grid, new_grid, start, end))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return new_grid
