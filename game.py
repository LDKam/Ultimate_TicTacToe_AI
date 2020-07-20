from __future__ import annotations

import copy
from typing import List, Set

from players.player import *


class UltimateTicTacToe:
    def __init__(self, dim: int = 3, verbose: bool = False):
        self.dim = dim
        self.verbose = verbose
        self.board = [[0] * (self.dim ** 2) for _ in range(self.dim ** 2)]
        self.maxiboard = [0 for _ in range(self.dim ** 2)]
        self.win_configs = self._find_win_configs()
        self.curr_mini_i = -1
        self.curr_player = 1
        self.winner = 0
        self.squares_left = self.dim ** 4

    def update(self, move: Move) -> None:
        """Updates the board, maxiboard, and miniboard states based on the move taken by the current player
        and prepares for the next move by the opposing player.
        """
        self.board[move[0]][move[1]] = self.curr_player  # board updated with the requested move
        self.curr_mini_i = move[0] if self.curr_mini_i == -1 else self.curr_mini_i
        if self.maxiboard[self.curr_mini_i] == 0 and self._is_board_won(self.board[self.curr_mini_i]):
            self.maxiboard[self.curr_mini_i] = self.curr_player
        if self._is_board_won(self.maxiboard):
            self.winner = self.curr_player
        self.squares_left -= 1
        if self.verbose:
            self.draw_board()

        self.curr_mini_i = move[1]
        self.curr_player *= -1

    def get_valid_miniboards_and_moves(self) -> Tuple[int, List[Move]]:
        """Gets all the possible moves as tuples for the current player.
        Note that all valid moves are contained in a single miniboard unless there are none in that miniboard.
        """
        valid_moves_in_miniboard = [(self.curr_mini_i, i) for i, s
                                    in enumerate(self.board[self.curr_mini_i]) if s == 0]
        if self.curr_mini_i == -1 or not valid_moves_in_miniboard:
            self.curr_mini_i = -1
            all_valid_moves = [(mini_i, i) for mini_i in range(9) for i, s in enumerate(self.board[mini_i]) if s == 0]
            return self.curr_mini_i, all_valid_moves

        return self.curr_mini_i, valid_moves_in_miniboard

    def get_curr_player(self) -> int:
        return self.curr_player

    def get_winner(self) -> int:
        return self.winner

    def get_maxiboard(self) -> List[int]:
        return self.maxiboard

    def get_miniboard(self, i) -> List[int]:
        return self.board[i]

    def get_board(self) -> List[List[int]]:
        return self.board

    def get_squares_left(self) -> int:
        return self.squares_left

    def set_verbose(self, verbose: bool) -> None:
        self.verbose = verbose

    def is_game_over(self) -> bool:
        """Determines whether a player has won, or there are no squares left.
        """
        if self.squares_left == 0 or self.winner != 0:
            return True
        return False

    def clone(self) -> UltimateTicTacToe:
        """Clones the game at the current state.
        """
        clone = copy.deepcopy(self)
        return clone

    def draw_board(self) -> None:
        """Draws the game state in text.
        """
        for i in range(3):
            print('-' * 3 * (3 + 1))
            for j in range(3):
                line = []
                for mini_i in range(3 * i, 3 * (i + 1)):
                    line.append('|')
                    for square_i in range(3 * j, 3 * (j + 1)):
                        if self.board[mini_i][square_i] == 1:
                            line.append('X')
                        elif self.board[mini_i][square_i] == -1:
                            line.append('O')
                        else:
                            line.append(' ')
                print(''.join(line))
        print('-' * 3 * (3 + 1))

    def reset(self) -> None:
        """Resets the game to the starting state.
        """
        self.board = [[0] * (self.dim ** 2) for _ in range(self.dim ** 2)]
        self.maxiboard = [0 for _ in range(self.dim ** 2)]
        self.curr_mini_i = -1
        self.curr_player = 1
        self.winner = 0
        self.squares_left = self.dim ** 4

    def _find_win_configs(self) -> List[Set[int]]:
        """Defines all the winning configurations of the tic-tac-toe board.
        """
        win_configs = []
        for i in range(self.dim):
            win_configs.append(set(range(self.dim * i, self.dim * (i + 1))))  # horizontals
            win_configs.append(set(range(i, self.dim ** 2, self.dim)))  # verticals
        win_configs.append(set(range(0, self.dim ** 2, self.dim + 1)))  # major diagonal
        win_configs.append(set(range(self.dim - 1, self.dim ** 2 - 1, self.dim - 1)))  # minor diagonal
        return win_configs

    def _is_board_won(self, board: List[int]) -> bool:
        """Determines whether the current player has won a previously unclaimed board.
        """
        claimed_squares = {i for i, s in enumerate(board) if s == self.curr_player}
        for config in self.win_configs:
            if config.issubset(claimed_squares):
                return True
        return False
