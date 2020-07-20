from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from game import UltimateTicTacToe

Move = Tuple[int, int]


class Player:
    IS_HUMAN = None

    def __init__(self, token: Optional[str] = None):
        self.token = token

    def get_token(self):
        return self.token

    def choose_move(self, game: UltimateTicTacToe) -> Move:
        raise NotImplementedError
