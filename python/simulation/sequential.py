from .step import *
import numpy as np

def run_sequential(grid, steps, allow_lightning=True):
    for i in range(steps):
        grid = step(grid, allow_lightning=(allow_lightning if i==0 else True))
    return grid
