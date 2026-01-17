from enum import Enum, auto
import random as rand
import os

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 512

class PixelState(Enum):
    EMPTY = auto()
    TREE = auto()
    BURNING = auto()

class Grid():
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.cells = [[PixelState.TREE for _ in range(width)]for _ in range(height)]

    def neighbours(self, x, y):
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                if dx == 0 and dy == 0:
                    continue
                    
                nx,ny = x+dx, y+dy
                if 0<=nx<self.width and 0<= ny<self.height:
                    yield nx,ny

    def start_fire(self):
        x = rand.randint(0,self.width)
        y = rand.randint(0,self.height)
        self.cells[x][y] = PixelState.BURNING
        return grid
    
def state_to_int(state):
    if state == PixelState.EMPTY:
        return 0
    if state == PixelState.TREE:
        return 1
    if state == PixelState.BURNING:
        return 2
    
def step(grid, p , g):
    new_grid = Grid(grid.height,grid.width)
    for y in range(grid.height):
        for x in range(grid.width):
            state = grid.cells[y][x]
            if state == PixelState.EMPTY:
                new_grid.cells[y][x] = PixelState.EMPTY
            elif state == PixelState.BURNING:
                new_grid.cells[y][x] = PixelState.EMPTY
            else:
                burning_neighbor = any(
                    grid.cells[ny][nx] == PixelState.BURNING
                    for nx, ny in grid.neighbours(x, y)
                )
                if burning_neighbor:
                    new_grid.cells[y][x] = PixelState.BURNING
                else:
                    new_grid.cells[y][x] = PixelState.TREE
    return new_grid

def start_fire(grid):
    x = rand.randint(0,SCREEN_WIDTH)
    y = rand.randint(0,SCREEN_HEIGHT)
    grid[x][y] = PixelState.BURNING
    return grid
    
def grid_to_file(grid, iter, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    filename= f"{output_dir}/iteration_{iter}.txt"
    with open(filename, mode="w") as f:
        for y in range(grid.height):
            row = [str(state_to_int(grid.cells[y][x])) for x in range(grid.width)]

            f.write(" ".join(row)+"\n")

if __name__ == '__main__':
    grid = Grid(SCREEN_HEIGHT, SCREEN_WIDTH)
    grid.start_fire()
    for i in range(100):
        grid_to_file(grid,i)
        grid=step(grid, p=0.0001,g=0.01)