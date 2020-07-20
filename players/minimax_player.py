from __future__ import annotations

from math import log2
from typing import List

from players.player import *


class MinimaxPlayer(Player):
    IS_HUMAN = False

    def __init__(self, token: Optional[str] = None, depth: Optional[int] = None, dim: int = 3):
        super().__init__(token)
        self.depth = depth if depth is not None else None
        self.dim = dim
        self.point_system = self._calculate_point_system()
        self.inf = sum(self.point_system) ** 2 + 1  # value greater than the maximum number of points possible

    def _calculate_point_system(self) -> List[int]:
        """Calculates a point system for each square based on the number of winning configurations
        that include the square. Edges, corners, and centers are worth two, three, and four points,
        respectively, in a standard ultimate tic-tac-toe board.
        """
        point_system = [2] * (self.dim ** 2)  # horizontals & verticals
        for r in range(self.dim):
            point_system[self.dim * r + r] += 1  # major diagonal
            point_system[self.dim * r + (self.dim - 1 - r)] += 1  # minor diagonal
        return point_system

    def choose_move(self, game: UltimateTicTacToe) -> Move:
        """Chooses a move that maximizes the evaluation function, estimated via minimax with alpha-beta pruning.
        The default depth is the square root of the number of available squares plus one,
        which is used to avoid exploring an excessive number of game states at the start.
        """
        depth = self.depth if self.depth is not None else int(log2(81 - game.get_squares_left() + 1)) + 1
        _, move = self.apply_minimax_with_alpha_beta(game, (-1 * self.inf, None), (self.inf, None), depth)
        return move

    def apply_minimax_with_alpha_beta(self, game: UltimateTicTacToe, alpha: Tuple[int, Optional[Move]],
                                      beta: Tuple[int, Optional[Move]], depth: int) -> Tuple[int, Optional[Move]]:
        """Applies minimax with alpha-beta pruning to efficiently search for moves that lead to optimal game states,
        according to the evaluation function. If first, the player maximizes its minimum evaluation.
        If second, the player minimizes its maximum evaluation.
        """
        if game.is_game_over() or depth == 0:
            return self.evaluate_state(game), None

        curr_player = game.get_curr_player()
        best_move = (-1 * curr_player * self.inf, None)
        _, moves = game.get_valid_miniboards_and_moves()
        for move in moves:
            clone = game.clone()
            clone.set_verbose(False)
            clone.update(move)
            tmp = self.apply_minimax_with_alpha_beta(clone, alpha, beta, depth - 1)[0], move
            if curr_player == 1:
                if best_move[0] < tmp[0]:
                    best_move = tmp
                if alpha[0] < best_move[0]:
                    alpha = best_move
            else:
                if best_move[0] > tmp[0]:
                    best_move = tmp
                if beta[0] > best_move[0]:
                    beta = best_move
            if alpha[0] >= beta[0]:
                break
        if curr_player == 1:
            return alpha
        else:
            return beta

    def evaluate_state(self, game: UltimateTicTacToe) -> int:
        """Evaluates a game state using the point system.
        """
        total = sum(self.point_system)
        maxiboard = game.get_maxiboard()
        if game.is_game_over():
            return game.get_winner() * (total ** 2)
        else:
            maxiboard_score = total * sum(value * player for value, player in zip(self.point_system, maxiboard))
            miniboard_score = sum(maxi_value * mini_value * player if maxiboard[mini_i] == 0 else 0
                                  for mini_i, maxi_value in enumerate(self.point_system)
                                  for mini_value, player in zip(self.point_system, game.get_miniboard(mini_i)))
            return maxiboard_score + miniboard_score
