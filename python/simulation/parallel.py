import numpy as np
from multiprocessing import Pool, cpu_count
from simulation.step import *

def _step_chunk(chunk):
    return step(chunk)

def step_parallel(grid, n_workers=None):
    if n_workers is None:
        n_workers = cpu_count()

    h, w = grid.shape
    chunk_size = h // n_workers
    chunks = []

    for i in range(n_workers):
        start = max(i*chunk_size - 1, 0)
        end = min((i+1)*chunk_size + 1, h)
        chunks.append((start, end, grid[start:end]))

    def _step_chunk(chunk):
        burning = (chunk == BURNING)
        tree = (chunk == TREE)
        empty = (chunk == EMPTY)

        fire_risk_tree = np.zeros_like(chunk, dtype=bool)
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dy == 0 and dx == 0:
                    continue
                shifted = np.zeros_like(chunk, dtype=bool)
                if dy >= 0:
                    ys = dy
                    ye = chunk.shape[0]
                    ys_src = 0
                    ye_src = chunk.shape[0] - dy
                else:
                    ys = 0
                    ye = chunk.shape[0] + dy
                    ys_src = -dy
                    ye_src = chunk.shape[0]
                if dx >= 0:
                    xs = dx
                    xe = chunk.shape[1]
                    xs_src = 0
                    xe_src = chunk.shape[1] - dx
                else:
                    xs = 0
                    xe = chunk.shape[1] + dx
                    xs_src = -dx
                    xe_src = chunk.shape[1]
                
                shifted[ys:ye, xs:xe] = burning[ys_src:ye_src, xs_src:xe_src]
                fire_risk_tree |= (shifted & (np.random.rand(*chunk.shape) < FIRE_SPREAD_CHANCE))

        new_chunk = chunk.copy()
        new_chunk[burning] = EMPTY
        new_chunk[tree & fire_risk_tree] = BURNING

        # Spontaneous lightning
        lightning = (np.random.rand(*chunk.shape) < LIGHTNING_CHANCE)
        new_chunk[(tree ) & lightning] = BURNING

        # Growth
        growth = (np.random.rand(*chunk.shape) < GROWTH_CHANCE)
        new_chunk[empty & growth] = TREE

        return new_chunk

    with Pool(n_workers) as pool:
        results = pool.map(_step_chunk, [c[2] for c in chunks])

    new_grid = np.empty_like(grid)
    for (start, end, _), result in zip(chunks, results):
        # remove ghost rows
        if start == 0:
            new_grid[start:end-1] = result[:-1]
        elif end == h:
            new_grid[start+1:end] = result[1:]
        else:
            new_grid[start+1:end-1] = result[1:-1]

    return new_grid
