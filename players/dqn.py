from __future__ import annotations

import random
from typing import Optional

from keras.layers import Conv2D, Dense, Flatten
from keras.models import Sequential, load_model
from keras.optimizers import Adam

import players.dqn_player as dp
from players.dqn_util import *
from game import UltimateTicTacToe


class DQN:
    ADAM_LR = 3e-4

    def __init__(self, dim: int, load: bool, model_dir: Optional[str] = None):
        self.dim = dim
        self.model_dir = model_dir
        self.input_shape = (self.dim ** 2, self.dim ** 2, 2)
        self.output_shape = None
        if load:
            self.model = load_model(self.model_dir)
        else:
            self.model = self._construct()
        print(self.model.summary())

    def _construct(self):
        model = Sequential()
        model.add(Conv2D(32, self.dim, padding="same", activation="relu", input_shape=self.input_shape))
        model.add(Conv2D(32, self.dim, padding="same", activation="relu"))
        model.add(Conv2D(128, self.dim, padding="same", activation="relu"))
        model.add(Conv2D(128, self.dim, padding="same", activation="relu"))
        model.add(Conv2D(256, self.dim, strides=(self.dim, self.dim), padding="valid", activation="relu"))
        model.add(Conv2D(256, self.dim, padding="same", activation="relu"))
        model.add(Flatten())
        model.add(Dense(self.dim ** 4))
        model.compile(optimizer=Adam(self.ADAM_LR), loss="mean_squared_error", metrics=["accuracy"])
        return model

    def get_dim(self):
        return self.dim

    def get_weights(self):
        return self.model.get_weights()

    def set_weights(self, weights) -> None:
        self.model.set_weights(weights)

    def evaluate(self, state: UltimateTicTacToe, to_board: bool = True):
        dqn_input = convert_board_to_dqn_input(self.dim, state)
        dqn_output = self.model.predict(dqn_input)
        if to_board:
            return convert_dqn_output_to_board(self.dim, dqn_output)
        return dqn_output

    def train(self, input_frames, q_truths) -> None:
        self.model.train_on_batch(input_frames, q_truths)

    def save(self) -> None:
        self.model.save(self.model_dir)


class DQNTrainer:
    def __init__(self, epochs: int, epsilon: float, dim: int, target: DQN):
        self.epochs = epochs
        self.epsilon = epsilon
        self.dim = dim
        self.batches = 32
        self.epoch_i = 0
        self.batch_i = 0
        self.batch_size = 64
        self.history = deque()
        self.buffer = ReplayBuffer(capacity=self.batch_size)
        self.gamma = 0.99
        self.target = target

    def record_move(self, move) -> None:
        self.history.append(move)

    def update(self):
        action_i = random.randrange(len(self.history))
        game = UltimateTicTacToe(verbose=False)
        for _ in range(action_i):
            game.update(self.history.popleft())
        self.buffer.push((game, self.history.popleft()))
        self.history.clear()

    def update_model(self, model: DQN):
        dqn_inputs = []
        q_truths = []
        while not self.buffer.is_empty():
            curr_state, move = self.buffer.pop()
            dqn_input = convert_board_to_dqn_input(self.dim, curr_state)
            dqn_inputs.append(dqn_input)
            q_truth = model.evaluate(curr_state, to_board=False)
            next_state = curr_state.clone()
            next_state.update(move)
            index = (self.dim ** 2) * move[0] + move[1]
            if next_state.is_game_over():
                winner = next_state.get_winner() * curr_state.get_curr_player()
                q_truth[0][index] = winner
            else:
                _, next_q_val = dp.DeepQLearningPlayer.find_q_move(self.target, next_state)
                q_truth[0][index] = self.gamma * next_q_val * -1
            q_truths.append(q_truth)

        dqn_inputs = np.concatenate(dqn_inputs)
        q_truths = np.concatenate(q_truths, axis=0)
        model.train(dqn_inputs, q_truths)
        self.batch_i += 1
        if self.batch_i == self.batches:
            self.target.set_weights(model.get_weights())
            self.target.save()
            self.epoch_i += 1
            print("Epoch " + str(self.epoch_i) + " is complete.")
            self.batch_i = 0
            if self.epoch_i == self.epochs:
                print("Training is complete.")

    def is_buffer_full(self) -> bool:
        return self.buffer.is_full()

    def is_epsilon_greedy(self) -> bool:
        if random.random() > self.epsilon:
            return True
        return False

    def is_training_complete(self):
        return self.epoch_i == self.epochs
