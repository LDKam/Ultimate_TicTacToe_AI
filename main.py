import sys

from game import *
from players.dqn_player import DeepQLearningPlayer
from players.human_player import HumanPlayer
from players.minimax_player import MinimaxPlayer
from players.random_player import RandomPlayer


def process_args(argv: List[str]) -> Tuple[Player, Player]:
    """Parse command line arguments to determine the players of the game.
    """
    if len(argv) != 3:
        player_1 = RandomPlayer()
        player_2 = RandomPlayer()
    else:
        str_1 = sys.argv[1]
        if str_1 == "-d":
            player_1 = DeepQLearningPlayer()
        elif str_1 == "-h":
            player_1 = HumanPlayer()
        elif str_1 == "-m":
            player_1 = MinimaxPlayer()
        else:
            player_1 = RandomPlayer()
        str_2 = sys.argv[2]
        if str_2 == "-d":
            player_2 = DeepQLearningPlayer()
        elif str_2 == "-h":
            player_2 = HumanPlayer()
        elif str_2 == "-m":
            player_2 = MinimaxPlayer()
        else:
            player_2 = RandomPlayer()
    return player_1, player_2


if __name__ == "__main__":
    """Plays AI vs. AI or human vs. AI. Use -d to refer to a deep q-learning player, -h to refer to a human player, 
    -m to refer to a minimax bot, and -r to refer to a random bot. With human players, use gui.py to play the game.
    """
    p1, p2 = process_args(sys.argv)
    p1_wins = 0
    p2_wins = 0
    ties = 0
    rounds = 100
    for i in range(rounds):
        game = UltimateTicTacToe(verbose=False)
        while not game.is_game_over():
            if game.get_curr_player() == 1:
                move = p1.choose_move(game)
            else:
                move = p2.choose_move(game)
            game.update(move)
        if game.get_winner() == 1:
            p1_wins += 1
        elif game.get_winner() == -1:
            p2_wins += 1
        else:
            ties += 1
        print("Round " + str(i + 1) + " over.")
    print("P1: " + str(p1_wins) + ", P2: " + str(p2_wins) + ", Ties: " + str(ties))
