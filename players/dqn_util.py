from collections import deque

import numpy as np

from game import UltimateTicTacToe


class ReplayBuffer:
    def __init__(self, capacity: int = 32):
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity

    def push(self, info) -> None:
        self.buffer.append(info)

    def pop(self):
        return self.buffer.pop()

    def is_full(self) -> bool:
        return len(self.buffer) == self.capacity

    def is_empty(self) -> bool:
        return len(self.buffer) == 0


def convert_board_to_dqn_input(dim: int, state: UltimateTicTacToe):
    board = state.get_board()
    curr_player = state.get_curr_player()
    arr_input = np.zeros(shape=(dim ** 2, dim ** 2, 2))
    for mini_i in range(dim ** 2):
        for square_i in range(dim ** 2):
            x = dim * (mini_i % dim) + square_i % dim
            y = dim * (mini_i // dim) + square_i // dim
            if board[mini_i][square_i] == state.get_curr_player():
                arr_input[y][x][0] = 1
            if board[mini_i][square_i] == state.get_curr_player() * -1:
                arr_input[y][x][1] = 1
    return np.expand_dims(arr_input * curr_player, axis=0)


def convert_dqn_output_to_board(dim: int, dqn_output: np.ndarray):
    board = [[None] * dim ** 2 for _ in range(dim ** 2)]
    for i in range(dim ** 4):
        miniboard_i = i // (dim ** 2)
        square_i = i % (dim ** 2)
        board[miniboard_i][square_i] = dqn_output[0][i]
    return board
