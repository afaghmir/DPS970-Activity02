import argparse
import math
from pathlib import Path

import connect_four as game
from mcts import monte_carlo_tree_search


def main():
    parser = argparse.ArgumentParser(description="Connect Four move generator (MCTS)")
    parser.add_argument("--position", default="data/positions/empty.txt")
    parser.add_argument("--cycles", type=int, default=500)
    parser.add_argument("--x", type=int, default=2, help="nodes to expand at each level")
    parser.add_argument("--height", type=int, default=4, help="tree height before playout")
    parser.add_argument("--c", type=float, default=math.sqrt(2), help="exploration constant")
    parser.add_argument("--w", type=float, default=0.5, help="weight of the objective part")
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    state = game.from_text(Path(args.position).read_text())
    move, tree = monte_carlo_tree_search(state, args.cycles, args.x, args.height,
                                         args.c, args.w, args.seed, return_tree=True)

    print(game.to_text(state))
    print("0123456")
    print(f"\nplayer to move: {game.SYMBOLS[state.to_move]}")
    print("column  playouts  win rate")
    for child in sorted(tree.children, key=lambda n: n.move):
        print(f"{child.move:6}  {child.N:8}  {child.U / child.N:8.2f}")
    print(f"\nchosen move: column {move}")


if __name__ == "__main__":
    main()
