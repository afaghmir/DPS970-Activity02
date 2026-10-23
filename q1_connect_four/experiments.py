import argparse
import csv
import math
import time
from collections import Counter
from pathlib import Path

import connect_four as game
from mcts import monte_carlo_tree_search

BASE = {"cycles": 500, "x": 2, "height": 4, "c": math.sqrt(2), "w": 0.5}

# change one setting at a time from the base settings
VARIATIONS = {
    "w": [0.0, 0.5, 2.0],
    "cycles": [50, 200, 1000],
    "x": [1, 3, 7],
    "height": [2, 4, 8],
}

POSITIONS = ["empty", "win", "block"]


def run(runs, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    states = {p: game.from_text(Path(f"data/positions/{p}.txt").read_text()) for p in POSITIONS}
    rows, summary = [], []

    for setting, values in VARIATIONS.items():
        for value in values:
            config = dict(BASE, **{setting: value})
            for name, state in states.items():
                moves, times = [], []
                for seed in range(runs):
                    start = time.perf_counter()
                    move = monte_carlo_tree_search(state, config["cycles"], config["x"],
                                                   config["height"], config["c"], config["w"], seed)
                    times.append(time.perf_counter() - start)
                    moves.append(move)
                    rows.append({"setting": setting, "value": value, "position": name,
                                 "seed": seed, "move": move, "seconds": round(times[-1], 4)})
                counts = Counter(moves)
                top_move, top_count = counts.most_common(1)[0]
                summary.append({"setting": setting, "value": value, "position": name,
                                "most_common_move": top_move,
                                "same_move_pct": round(100 * top_count / runs),
                                "distinct_moves": len(counts),
                                "move_counts": dict(sorted(counts.items())),
                                "avg_seconds": round(sum(times) / runs, 3)})
                print(f"{setting}={value:<6} {name:6} move {top_move} "
                      f"{100 * top_count / runs:5.0f}%  moves {dict(sorted(counts.items()))}")

    with open(out_dir / "runs.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    with open(out_dir / "summary.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary[0].keys())
        writer.writeheader()
        writer.writerows(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MCTS experiments")
    parser.add_argument("--runs", type=int, default=20, help="runs per setting and position")
    parser.add_argument("--out", default="results")
    args = parser.parse_args()
    run(args.runs, Path(args.out))
