import numpy as np

EMPTY = np.uint8(0)
TREE = np.uint8(1)
BURNING = np.uint8(2)
THICK_TREE = np.uint(3)

COLORS = {
    EMPTY: (0, 0, 0),
    TREE: (34, 139, 34),
    BURNING: (255, 69, 0),
    THICK_TREE: (29, 109, 18)
}

GROWTH_CHANCE = 0.01
LIGHTNING_CHANCE = 0.0001
FIRE_SPREAD_CHANCE = 0.3
FIRE_SPREAD_CHANCE_THICK = 0.15