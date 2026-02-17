import pygame
import numpy as np
from simulation.const import COLORS

from simulation.sequential import run_sequential
from simulation.parallel import *

CELL_SIZE = 1
FPS = 60

def run_live_viewer(grid, steps=1000, parallel=False, fps=60):
    pygame.init()
    height, width = grid.shape
    window_size = (width, height)
    screen = pygame.display.set_mode(window_size)
    clock = pygame.time.Clock()

    for step_idx in range(steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        if parallel:
            grid = step_parallel(grid)
        else:
            grid = run_sequential(grid, 1)

        surf = np.zeros((height, width, 3), dtype=np.uint8)
        for val, color in COLORS.items():
            surf[grid == val] = color

        pygame.surfarray.blit_array(screen, surf)
        pygame.display.flip()

        clock.tick(fps)