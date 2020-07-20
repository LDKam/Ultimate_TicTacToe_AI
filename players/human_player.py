from __future__ import annotations

from players.player import *


class HumanPlayer(Player):
    IS_HUMAN = True

    def __init__(self, token: Optional[str] = None):
        super().__init__(token)

    def choose_move(self, game: UltimateTicTacToe) -> Move:
        """Chooses a move requested by the user.
        """
        pass  # not used in GUI
