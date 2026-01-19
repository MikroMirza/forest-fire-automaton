import numpy as np
from multiprocessing import Pool, cpu_count, shared_memory
from simulation.const import *

def _worker(args):
    start, end, shape, dtype, shm_name = args

    shm = shared_memory.SharedMemory(name=shm_name)
    grid = np.ndarray(shape, dtype=dtype, buffer=shm.buf)

    chunk = grid[start:end].copy()
    burning = (chunk == BURNING)
    tree = (chunk == TREE)
    empty = (chunk == EMPTY)

    padded_burning = np.pad(burning, pad_width=1, mode='constant', constant_values=False)

    fire_risk_tree = np.zeros_like(chunk, dtype=bool)
    for dy in [0, 1, 2]:
        for dx in [0, 1, 2]:
            if dy == 1 and dx == 1:
                continue
            fire_risk_tree |= padded_burning[dy:dy + chunk.shape[0], dx:dx + chunk.shape[1]] & (
                np.random.rand(*chunk.shape) < FIRE_SPREAD_CHANCE
            )

    new_chunk = chunk.copy()
    new_chunk[burning] = EMPTY
    new_chunk[tree & fire_risk_tree] = BURNING

    lightning = (np.random.rand(*chunk.shape) < LIGHTNING_CHANCE)
    new_chunk[tree & lightning] = BURNING

    growth = (np.random.rand(*chunk.shape) < GROWTH_CHANCE)
    new_chunk[empty & growth] = TREE

    shm.close()
    return start, end, new_chunk

def step_parallel(grid, n_workers=None):
    if n_workers is None:
        n_workers = cpu_count()

    h, w = grid.shape
    chunk_h = h // n_workers
    chunks_args = []

    shm = shared_memory.SharedMemory(create=True, size=grid.nbytes)
    shm_grid = np.ndarray(grid.shape, dtype=grid.dtype, buffer=shm.buf)
    np.copyto(shm_grid, grid)

    for i in range(n_workers):
        start = max(i * chunk_h - 1, 0)
        end = min((i + 1) * chunk_h + 1, h)
        chunks_args.append((start, end, grid.shape, grid.dtype, shm.name))

    with Pool(n_workers) as pool:
        results = pool.map(_worker, chunks_args)

    new_grid = np.empty_like(grid)
    for start, end, chunk in results:
        if start == 0:
            new_grid[start:end - 1] = chunk[:-1]
        elif end == h:
            new_grid[start + 1:end] = chunk[1:]
        else:
            new_grid[start + 1:end - 1] = chunk[1:-1]

    shm.close()
    shm.unlink()
    return new_grid