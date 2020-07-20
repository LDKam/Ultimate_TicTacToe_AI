import sys

from game import *
from players.dqn_player import DeepQLearningPlayer

if __name__ == "__main__":
    """Trains the deep q-learning agent via self-play.
    """
    num_epochs = 10
    if len(sys.argv) == 2:
        if sys.argv[1].isnumeric():
            num_epochs = int(sys.argv[1])
    player_x = DeepQLearningPlayer(load=False, train=True, epochs=num_epochs)
    player_o = player_x
    while not player_x.is_training_complete():
        game = UltimateTicTacToe(verbose=False)
        while not game.is_game_over():
            if game.get_curr_player() == 1:
                move = player_x.choose_move(game)
            else:
                move = player_o.choose_move(game)
            game.update(move)
        player_x.update_trainer()
