from game import UltimateTicTacToe
from players.player import Player


def is_curr_player_human(game: UltimateTicTacToe, p1: Player, p2: Player) -> bool:
    return (game.get_curr_player() == 1 and p1.IS_HUMAN) or (game.get_curr_player() == -1 and p2.IS_HUMAN)
