import numpy as np
from numba import njit, prange
from simulation.const import *

@njit(parallel=True)
def step_parallel(grid):
    h, w = grid.shape
    new_grid = grid.copy()

    for y in prange(h):
        for x in range(w):

            cell = grid[y, x]
            if cell == BURNING:
                new_grid[y, x] = EMPTY
                continue

            if cell == TREE:

                fire_neighbor = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dy == 0 and dx == 0:
                            continue

                        ny = y + dy
                        nx = x + dx

                        if 0 <= ny < h and 0 <= nx < w:
                            if grid[ny, nx] == BURNING:
                                if np.random.random() < FIRE_SPREAD_CHANCE:
                                    fire_neighbor = True

                if fire_neighbor:
                    new_grid[y, x] = BURNING
                    continue

                if np.random.random() < LIGHTNING_CHANCE:
                    new_grid[y, x] = BURNING
                    continue

            if cell == EMPTY:
                if np.random.random() < GROWTH_CHANCE:
                    new_grid[y, x] = TREE

    return new_grid
