import numpy as np
from .const import *

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
    new_grid[tree & (np.random.rand(*grid.shape) < LIGHTNING_CHANCE)] = BURNING
    new_grid[empty & (np.random.rand(*grid.shape) < GROWTH_CHANCE)] = TREE

    return new_grid

def step_chunk(chunk):
    return step(chunk)

