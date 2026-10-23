import math
import random

import connect_four as game


class Node:
    # a node in the search tree
    def __init__(self, state, parent=None, move=None):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.untried = list(game.actions(state))
        self.depth = 0 if parent is None else parent.depth + 1
        self.U = 0.0
        self.N = 0


def score(node, c, w):
    # utility = ucb1 (playout part) + w * eval (objective part)
    parent = node.parent
    mover = parent.state.to_move
    exploit = node.U / node.N
    explore = c * math.sqrt(math.log(parent.N) / node.N)
    objective = game.eval_normalized(node.state, mover)
    return exploit + explore + w * objective


def select(tree, height, c, w):
    # go down while the node is fully expanded and above the height limit
    node = tree
    while not node.untried and node.children and node.depth < height:
        node = max(node.children, key=lambda child: score(child, c, w))
    return node


def expand(leaf, x, height, rng):
    # add up to x new children, no growth past the height limit
    if not leaf.untried or leaf.depth >= height:
        return [leaf]
    moves = rng.sample(leaf.untried, min(x, len(leaf.untried)))
    new_children = []
    for move in moves:
        leaf.untried.remove(move)
        child = Node(game.result(leaf.state, move), leaf, move)
        leaf.children.append(child)
        new_children.append(child)
    return new_children


def simulate(node, rng):
    # random playout policy until the game ends
    state = node.state
    while not game.is_terminal(state):
        state = game.result(state, rng.choice(game.actions(state)))
    return game.winner(state)


def back_propagate(result, node):
    # each node stores utility for the player who made the move into it
    while node is not None:
        node.N += 1
        if node.parent is not None:
            mover = node.parent.state.to_move
            if result is None:
                node.U += 0.5
            elif result == mover:
                node.U += 1.0
        node = node.parent


def monte_carlo_tree_search(state, cycles=500, x=2, height=4, c=math.sqrt(2), w=0.5,
                            seed=None, return_tree=False):
    # figure 5.11, repeated a fixed number of cycles
    rng = random.Random(seed)
    tree = Node(state)
    for _ in range(cycles):
        leaf = select(tree, height, c, w)
        for child in expand(leaf, x, height, rng):
            result = simulate(child, rng)
            back_propagate(result, child)
    best = max(tree.children, key=lambda child: child.N)
    if return_tree:
        return best.move, tree
    return best.move
