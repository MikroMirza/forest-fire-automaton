import time 
import numpy as np

from simulation.step import step
from simulation.const import *
from io.writer import grid_to_file
HEIGHT = 512
WIDTH = 512
STEPS = 500

if __name__ == '____':
    np.random.seed(1389)

    grid = np.ones((HEIGHT,WIDTH), dtype=np.uint8)* TREE

    x = np.random.randint(0,WIDTH)
    y = np.random.randint(0,HEIGHT)
    grid[y,x] = BURNING

    start = time.perf_counter()

    for i in range(STEPS):
        grid_to_file(grid,i,"output_seq")
        grid = step(grid)
    
    end = time.perf_counter()

    with open("output_seq/timing.txt", "w") as f:
        f.write(f"Sequential program runtime {end-start} seconds\n")