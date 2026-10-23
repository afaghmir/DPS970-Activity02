import random
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import connect_four as game
from mcts import Node, back_propagate, expand, monte_carlo_tree_search, select

POSITIONS = ROOT / "data" / "positions"


def load(name):
    return game.from_text((POSITIONS / f"{name}.txt").read_text())


def play(moves):
    state = game.initial_state()
    for col in moves:
        state = game.result(state, col)
    return state


def nodes(tree):
    stack = [tree]
    while stack:
        node = stack.pop()
        yield node
        stack.extend(node.children)


class TestGame(unittest.TestCase):

    def test_initial_state(self):
        state = game.initial_state()
        self.assertEqual(game.to_move(state), game.P1)
        self.assertEqual(game.actions(state), list(range(7)))

    def test_piece_drops_to_lowest_cell(self):
        state = play([3, 3])
        self.assertEqual(state.board[0][3], game.P1)
        self.assertEqual(state.board[1][3], game.P2)

    def test_full_column_not_legal(self):
        state = play([0, 0, 0, 0, 0, 0])
        self.assertNotIn(0, game.actions(state))

    def test_horizontal_win(self):
        self.assertEqual(game.winner(play([0, 0, 1, 1, 2, 2, 3])), game.P1)

    def test_vertical_win(self):
        self.assertEqual(game.winner(play([0, 1, 0, 1, 0, 1, 0])), game.P1)

    def test_diagonal_win(self):
        self.assertEqual(game.winner(play([0, 1, 1, 2, 2, 3, 2, 3, 3, 6, 3])), game.P1)

    def test_draw_board_is_terminal(self):
        # columns filled so no line of four is made
        order = [0, 1, 2, 3, 4, 5, 6] * 2 + [1, 0, 3, 2, 5, 4, 6] * 2 + [0, 1, 2, 3, 4, 5, 6] * 2
        state = game.initial_state()
        for col in order:
            state = game.result(state, col)
        self.assertTrue(game.is_terminal(state))
        self.assertIsNone(game.winner(state))
        self.assertEqual(game.utility(state, game.P1), 0.5)

    def test_utility(self):
        state = play([0, 0, 1, 1, 2, 2, 3])
        self.assertEqual(game.utility(state, game.P1), 1.0)
        self.assertEqual(game.utility(state, game.P2), 0.0)

    def test_eval_prefers_player_with_threats(self):
        state = load("win")
        self.assertGreater(game.evaluate(load("block"), game.P2), 0)
        self.assertEqual(game.evaluate(game.initial_state(), game.P1), 0)
        self.assertEqual(game.evaluate(state, game.P1), -game.evaluate(state, game.P2))

    def test_positions_load(self):
        self.assertEqual(game.to_move(load("win")), game.P1)
        self.assertEqual(game.to_move(load("block")), game.P1)
        self.assertEqual(game.to_text(load("empty")), "\n".join(["......."] * 6))


class TestMCTSSteps(unittest.TestCase):

    def test_expand_adds_x_children(self):
        tree = Node(game.initial_state())
        children = expand(tree, 3, 4, random.Random(0))
        self.assertEqual(len(children), 3)
        self.assertEqual(len(tree.untried), 4)

    def test_no_expansion_past_height(self):
        leaf = Node(game.initial_state())
        leaf.depth = 4
        self.assertEqual(expand(leaf, 3, 4, random.Random(0)), [leaf])

    def test_back_propagate_updates_path(self):
        tree = Node(game.initial_state())
        child = expand(tree, 1, 4, random.Random(0))[0]
        back_propagate(game.P1, child)
        self.assertEqual((tree.N, child.N, child.U), (1, 1, 1.0))
        back_propagate(game.P2, child)
        self.assertEqual((tree.N, child.N, child.U), (2, 2, 1.0))

    def test_select_stops_at_node_with_untried_moves(self):
        tree = Node(game.initial_state())
        self.assertIs(select(tree, 4, 1.4, 0.5), tree)


class TestMoveGenerator(unittest.TestCase):

    def test_takes_winning_move(self):
        self.assertEqual(monte_carlo_tree_search(load("win"), cycles=300, seed=1), 3)

    def test_blocks_opponent_win(self):
        self.assertEqual(monte_carlo_tree_search(load("block"), cycles=500, seed=1), 3)

    def test_returns_legal_move(self):
        state = load("empty")
        for seed in range(5):
            self.assertIn(monte_carlo_tree_search(state, cycles=50, seed=seed), game.actions(state))

    def test_tree_never_grows_past_height(self):
        _, tree = monte_carlo_tree_search(load("empty"), cycles=300, x=3, height=2,
                                          seed=0, return_tree=True)
        self.assertLessEqual(max(n.depth for n in nodes(tree)), 2)

    def test_number_of_playouts(self):
        # every cycle runs one playout per new child, so the root counts them all
        _, tree = monte_carlo_tree_search(load("empty"), cycles=100, x=2, height=3,
                                          seed=0, return_tree=True)
        self.assertEqual(tree.N, sum(child.N for child in tree.children))
        self.assertGreaterEqual(tree.N, 100)

    def test_same_seed_same_move(self):
        a = monte_carlo_tree_search(load("empty"), cycles=200, seed=7)
        b = monte_carlo_tree_search(load("empty"), cycles=200, seed=7)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
