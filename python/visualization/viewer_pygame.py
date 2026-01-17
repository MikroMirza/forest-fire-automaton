import pygame
import numpy as np
from simulation.const import COLORS
from simulation.sequential import run_sequential  # or your step_parallel

CELL_SIZE = 2
FPS = 60

def run_live_viewer(grid, steps=1000):
    pygame.init()
    height, width = grid.shape
    screen = pygame.display.set_mode((width * CELL_SIZE, height * CELL_SIZE))
    clock = pygame.time.Clock()
    surface = pygame.Surface((width, height))

    for _ in range(steps):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        grid = run_sequential(grid, 1)

        rgb = np.zeros((width, height, 3), dtype=np.uint8)
        for state, color in COLORS.items():
            rgb[grid == state] = color

        pygame.surfarray.blit_array(surface, rgb.swapaxes(0, 1))
        pygame.transform.scale(surface, screen.get_size(), screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
