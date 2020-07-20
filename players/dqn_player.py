from __future__ import annotations

from players.dqn import *
from players.player import Move, Player


class DeepQLearningPlayer(Player):
    IS_HUMAN = False

    def __init__(self, load: bool = True, token: Optional[str] = None, model_dir: str = "dqn_model",
                 dim: int = 3, train: bool = False, epochs: int = 100, epsilon: float = 0.2):
        super().__init__(token)
        self.model_dir = model_dir
        self.model = DQN(dim, load, model_dir=self.model_dir)
        if train:
            target = DQN(dim, load, model_dir=self.model_dir)
            target.set_weights(self.model.get_weights())
            self.trainer = DQNTrainer(epochs, epsilon, dim, target)
        else:
            self.trainer = None

    def choose_move(self, game: UltimateTicTacToe) -> Move:
        """Chooses an appropriate move for the player, either the best-value move for the player or a random move
        if the player is exploring under epsilon-greedy training. Records the move if the player is training.
        """
        if self.trainer is not None and self.trainer.is_epsilon_greedy():
            _, valid_moves = game.get_valid_miniboards_and_moves()
            selected_move = random.choice(valid_moves)
        else:
            selected_move, _ = self.find_q_move(self.model, game)
        if self.trainer is not None:
            self.trainer.record_move(selected_move)
        return selected_move

    def update_trainer(self) -> None:
        """Updates the trainer by updating the target model at the end of the game if the buffer contains a full batch.
        """
        if self.trainer is None:
            return
        self.trainer.update()
        if self.trainer.is_buffer_full():
            self.trainer.update_model(self.model)

    def is_training_complete(self) -> bool:
        return self.trainer.is_training_complete()

    @staticmethod
    def find_q_move(model: DQN, state: UltimateTicTacToe):
        """Finds the move that leads to the best value for the player, estimated with a neural net.
        """
        q_vals = model.evaluate(state, to_board=True)
        best_action = None
        best_value = float("-inf")
        _, valid_moves = state.get_valid_miniboards_and_moves()
        for move in valid_moves:
            q_val = q_vals[move[0]][move[1]]
            if q_val > best_value:
                best_action = move
                best_value = q_val
        return best_action, best_value
