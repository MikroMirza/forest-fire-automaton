import numpy as np
from experimental.CLI import parse_args
from simulation.sequential import run_sequential
from simulation.parallel import step_parallel
from IO.writer import save_grid
from visualization.viewer_pygame import run_live_viewer
from simulation.const import *
import os
frame_dir = "frames"

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


def main():
    args = parse_args()

    grid = np.random.choice(
        [EMPTY, TREE],
        size=(args.height, args.width),
        p=[0.2, 0.8]
    )
    if args.strike_x is not None and args.strike_y is not None:
        x,y = args.strike_x,args.strike_y
        if 0<= x <=args.width and 0<=x <= args.height:
            grid[y,x] = BURNING
        else:
            print(f"Strike coordinates ({x},{y}) out of bounds")
    if args.save:
        for i in range(args.steps):
            if args.parallel:
                grid = step_parallel(grid)
            else:
                grid = run_sequential(grid, 1)
            save_grid(grid, i)
    else:
        run_live_viewer(grid, args.steps)



if __name__ == "__main__":
    main()
