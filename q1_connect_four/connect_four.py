from dataclasses import dataclass

ROWS, COLS = 6, 7
EMPTY, P1, P2 = 0, 1, 2
SYMBOLS = {EMPTY: ".", P1: "X", P2: "O"}


@dataclass(frozen=True)
class State:
    # board[r][c], row 0 is the bottom row
    board: tuple
    to_move: int
    last_move: tuple = None


def other(player):
    return P2 if player == P1 else P1


def initial_state():
    return State(tuple(tuple(EMPTY for _ in range(COLS)) for _ in range(ROWS)), P1)


def to_move(state):
    return state.to_move


def actions(state):
    # a column is legal if its top cell is empty
    if is_terminal(state):
        return []
    return [c for c in range(COLS) if state.board[ROWS - 1][c] == EMPTY]


def result(state, col):
    # drop the piece into the lowest empty cell of the column
    for r in range(ROWS):
        if state.board[r][col] == EMPTY:
            rows = [list(row) for row in state.board]
            rows[r][col] = state.to_move
            board = tuple(tuple(row) for row in rows)
            return State(board, other(state.to_move), (r, col))
    raise ValueError(f"column {col} is full")


def winner(state):
    # only the last move can create a new line of four
    if state.last_move is None:
        return None
    r, c = state.last_move
    player = state.board[r][c]
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        count = 1
        for sign in (1, -1):
            rr, cc = r + sign * dr, c + sign * dc
            while 0 <= rr < ROWS and 0 <= cc < COLS and state.board[rr][cc] == player:
                count += 1
                rr += sign * dr
                cc += sign * dc
        if count >= 4:
            return player
    return None


def is_full(state):
    return all(state.board[ROWS - 1][c] != EMPTY for c in range(COLS))


def is_terminal(state):
    return winner(state) is not None or is_full(state)


def utility(state, player):
    # 1 win, 0 loss, 0.5 draw
    w = winner(state)
    if w is None:
        return 0.5
    return 1.0 if w == player else 0.0


def windows():
    # every line of 4 cells on the board
    lines = []
    for r in range(ROWS):
        for c in range(COLS):
            for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
                cells = [(r + i * dr, c + i * dc) for i in range(4)]
                if all(0 <= rr < ROWS and 0 <= cc < COLS for rr, cc in cells):
                    lines.append(cells)
    return lines


WINDOWS = windows()

# weights for the evaluation features
W_TWO, W_THREE, W_CENTER = 2, 5, 3


def evaluate(state, player):
    # weighted sum of features from the rules: open 2s, open 3s, center pieces
    opp = other(player)
    score = 0
    for cells in WINDOWS:
        values = [state.board[r][c] for r, c in cells]
        mine, theirs = values.count(player), values.count(opp)
        if theirs == 0:
            score += W_THREE * (mine == 3) + W_TWO * (mine == 2)
        if mine == 0:
            score -= W_THREE * (theirs == 3) + W_TWO * (theirs == 2)
    center = COLS // 2
    for r in range(ROWS):
        if state.board[r][center] == player:
            score += W_CENTER
        elif state.board[r][center] == opp:
            score -= W_CENTER
    return score


def eval_normalized(state, player, scale=50.0):
    # keep the objective part between -1 and 1
    return max(-1.0, min(1.0, evaluate(state, player) / scale))


def from_text(text):
    # top line of the text is the top row of the board
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if len(lines) != ROWS or any(len(line) != COLS for line in lines):
        raise ValueError("board must be 6 lines of 7 characters")
    lookup = {".": EMPTY, "X": P1, "O": P2}
    board = tuple(tuple(lookup[ch] for ch in line) for line in reversed(lines))
    x = sum(row.count(P1) for row in board)
    o = sum(row.count(P2) for row in board)
    return State(board, P1 if x == o else P2)


def to_text(state):
    return "\n".join("".join(SYMBOLS[v] for v in row) for row in reversed(state.board))
