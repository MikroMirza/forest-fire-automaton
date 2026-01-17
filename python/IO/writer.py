import os
import numpy as np

def save_grid(grid, step, out_dir="frames"):
    os.makedirs(out_dir, exist_ok=True)
    np.save(f"{out_dir}/frame_{step:05d}.npy", grid)
