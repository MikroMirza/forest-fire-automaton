import numpy as np
from .const import *
from multiprocessing import Pool, cpu_count

def step(grid, allow_lightning=True):
    burning = (grid == BURNING)
    tree = (grid == TREE)
    empty = (grid == EMPTY)

    padded_burning = np.pad(burning, pad_width=1, mode='constant', constant_values=False)

    fire_risk_tree = np.zeros_like(grid, dtype=bool)
    for dy in [0,1,2]:
        for dx in [0,1,2]:
            if dy == 1 and dx == 1:
                continue
            fire_risk_tree |= (padded_burning[dy:dy+grid.shape[0], dx:dx+grid.shape[1]] &
                               (np.random.rand(*grid.shape) < FIRE_SPREAD_CHANCE))



    new_grid = grid.copy()
    new_grid[burning] = EMPTY
    new_grid[tree & fire_risk_tree] = BURNING

    if allow_lightning:
        lightning = (np.random.rand(*grid.shape) < LIGHTNING_CHANCE)
        new_grid[(tree) & lightning] = BURNING

    growth = (np.random.rand(*grid.shape) < GROWTH_CHANCE)
    new_grid[empty & growth] = TREE

    return new_grid

def step_chunk(chunk):
    return step(chunk)


def step_parallel(grid, n_workers=None):
    if n_workers is None:
        n_workers = cpu_count()

    chunks = split_grid_with_ghosts(grid, n_workers)

    with Pool(n_workers) as pool:
        results = pool.map(step_chunk, [c[3] for c in chunks])

    new_grid = np.empty_like(grid)

    for (i, start, end, _), result in zip(chunks, results):
        if start == 0:
            trimmed = result[:-1]
            new_grid[start:end-1] = trimmed
        elif end == grid.shape[0]:
            trimmed = result[1:]
            new_grid[start+1:end] = trimmed
        else:
            trimmed = result[1:-1]
            new_grid[start+1:end-1] = trimmed

    return new_grid

def split_grid_with_ghosts(grid, n_workers):
    h = grid.shape[0]
    chunk_size = h // n_workers
    chunks = []

    for i in range(n_workers):
        start = max(i * chunk_size - 1, 0)
        end = min((i + 1) * chunk_size + 1, h)
        chunks.append((i, start, end, grid[start:end]))

    return chunks