import argparse

def parse_args():
    parser = argparse.ArgumentParser("Forest Fire Automaton")

    parser.add_argument("--width", type=int, default=200)
    parser.add_argument("--height", type=int, default=200)
    parser.add_argument("--steps", type=int, default=1000)

    parser.add_argument("--parallel", action="store_true")
    parser.add_argument("--save", action="store_true")

    parser.add_argument("--strike-x", type=int, default=None)
    parser.add_argument("--strike-y", type=int, default=None)

    parser.add_argument("--p-growth", type=float, default=0.01)
    parser.add_argument("--p-lightning", type=float, default=0.0001)

    return parser.parse_args()
