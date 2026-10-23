# DPS970 - Activity 2

Seyedeh Afagh Mirdehghan

- GitHub repo: https://github.com/afaghmir/DPS970-Activity02
- Test results (GitHub Actions): https://github.com/afaghmir/DPS970-Activity02/actions

![tests](https://github.com/afaghmir/DPS970-Activity02/actions/workflows/tests.yml/badge.svg)

## How to run

Python 3, no extra packages.

```
cd q1_connect_four
python3 main.py
python3 -m unittest discover -s tests -v
python3 experiments.py
```

- `main.py`: picks a move for `data/positions/empty.txt`
- Other settings: `python3 main.py --position data/positions/block.txt --cycles 1000 --x 3 --height 4 --w 0.5`
- `experiments.py`: 20 runs per setting on 3 boards, saved to `results/runs.csv` and `results/summary.csv`
- Test boards: `data/positions/` (empty, win, block)

## Q1 - Connect Four (MCTS)

- Based on Figure 5.11: select, expand, simulate, back-propagate
- Selection: utility = UCB1 (playout part) + W x Eval (objective part)
- Eval: open 2s (x2), open 3s (x5), center column pieces (x3)
- Expansion: x children per level
- Simulation: random playout once the tree reaches height H
- Repeated for a set number of cycles, returns the move with the most playouts
- Base settings: cycles 500, x 2, H 4, C 1.41, W 0.5

Results (empty board, 20 runs each):

| Setting | Same move |
|---|---|
| W = 0 / 0.5 / 2 | 75% / 100% / 100% |
| cycles = 50 / 200 / 1000 | 45% / 75% / 100% |
| x = 1 / 3 / 7 | 80% / 100% / 100% |
| H = 2 / 4 / 8 | 90% / 100% / 100% |

- Win and block boards: column 3 every time, in every setting
- Not always the same move: random playouts give different results each run
- More cycles, W > 0, bigger x or H give more consistent moves
- Forced moves (win, block) are always found

## Q2 - Validity

- (a) Smoke ⇒ Fire: **neither** (false only when Smoke = T, Fire = F)
- (b) ((Smoke ∧ Heat) ⇒ Fire) ⇔ ((Smoke ⇒ Fire) ∨ (Heat ⇒ Fire)): **valid** (true in all 8 rows)

## Q3 - Models

- 4 symbols → 16 models in total
- (a) B ∨ C: **12 models** (3 B/C combinations x 4 for A, D)
- (b) (A ⇒ B) ∧ A ∧ ¬B ∧ C ∧ D: **0 models** (A = T, B = F makes A ⇒ B false)

## Q4 - Resolution

- (a) **Valid** (true in all 8 rows)
- (b) Both sides in CNF: ¬Food ∨ ¬Drinks ∨ Party
  - Same clause → sentence is α ⇒ α → valid
- (c) Negation clauses: ¬Food ∨ ¬Drinks ∨ Party, Food, Drinks, ¬Party
  - → ¬Drinks ∨ Party → Party → empty clause
  - Negation unsatisfiable → **valid**

Full working (truth tables, CNF steps) is in the PDF.
