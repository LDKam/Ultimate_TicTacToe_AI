from __future__ import annotations

import random

from players.player import *


class RandomPlayer(Player):
    IS_HUMAN = False

    def __init__(self, token: Optional[str] = None, seed: Optional[int] = None):
        super().__init__(token)
        self.random_gen = random.Random()
        if seed is not None:
            self.random_gen.seed(seed)

    def choose_move(self, game: UltimateTicTacToe) -> Move:
        """Chooses a random move.
        """
        _, valid_moves = game.get_valid_miniboards_and_moves()
        return self.random_gen.choice(valid_moves)