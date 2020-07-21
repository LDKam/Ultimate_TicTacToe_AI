# Ultimate Tic-Tac-Toe Project
Ultimate tic-tac-toe is a variant of tic-tac-toe that contains nine tic-tac-toe boards embedded in the squares of a larger tic-tac-toe board. 
In this project, we refer to the smaller boards as miniboards and the larger board as maxiboard.
The game operates under the following rules:

* The game ends when a player wins the maxiboard under usual winning tic-tac-toe configurations.
* Players claim a square of the maxiboard when they win the corresponding miniboard. The squares of the miniboard remain available for play after the miniboard is won or lost, 
although they can longer affect the outcome of the miniboard.
* The current player must play in the miniboard of the maxiboard corresponding to the square of the miniboard that was last played by the opponent. 
For example, if a player places a token on the top-right square of a miniboard, then the opponent must place a token on a square of the top-right miniboard. 
If it is the first turn or there are no valid squares, the player may place a token anywhere on the board.

See the Wikipedia page for more information ([https://en.wikipedia.org/wiki/Ultimate_tic-tac-toe]).

## Overview
I implemented several agents (human, random, minimax, deep q-learning) and a basic GUI to play ultimate tic-tac-toe. 
A description and command-line argument for each agent is shown below:

* Human (-h): you select a move, either through text input for `main.py` or mouse input for `gui.py`.
* Random (-r): the agent selects move randomly from all the available moves.
* Minimax (-m): the agent selects a move using minimax with alpha-beta pruning of depth increasing with move count (on a log scale). 
See `player/minimax_player.py` for more information.
    * The values of the squares in unclaimed miniboards are weighted by the number of winning configurations in the miniboard and maxiboard that contain them. 
    For example, the center square in the top-right miniboard is worth 4 &times; 3 = 12 points 
    because there are four winning configurations in the miniboard that contain the center square 
    and three winning configurations in the maxiboard that contain the top-right miniboard. 
    The values of the squares in claimed miniboards is 0 since they not longer have an impact on the maxiboard; 
    however, a square in the maxiboard is weighted by the number of winning configurations in the maxiboard that contains them 
    scaled by all the squares in the corresponding miniboard. For example, the center square in the maxiboard is worth 4 &times; 24 = 96 points.
* DQN (-d): the agent selects a move by inputting the game state into a deep convolutional neural network that outputs a value for each potential (but usually illegal) move. 
The maximal valid move is chosen in practice, whereas a random move may be chosen in epsilon-greedy training. 
See `players/dqn_player.py` and `players/dqn.py` for more information.
    * The network uses six convolutional layers and a dense layer to take advantage of the spatial layout of ultimate tic-tac-toe.
    * The network in `dqn_model` was trained on self-play with a double deep q-learning approach, where the current model attempts to fit to a target model during each epoch 
    before the target model is updated by the current model at the end of the epoch, for 25 epochs. 
    Furthermore, only a single state per game is added to a batch to avoid training on correlated data.

The performances of two agents can be compared with `main.py`; 
for example, `python main.py -r -m` plays 100 rounds with the random agent as player 1 and the minimax agent as player 2, returning the number of games won, lost, and tied. 
The playstyles of the agents can be visualized with `gui.py`; for example `python gui.py -r -m` opens a GUI with the random agent as player 1 and the minimax agent as player 2. 
The user can play in the GUI by adding the '-h' command line argument appropriately. The GUI supports the following inputs:
* s (key): starts the game.
* r (key): resets the game.
* press (mouse): selects a move (which operates only when the user is playing).
The valid moves are highlighted on the board for each turn.

See `requirements.txt` for the list of required packages.

## Results
I compared the performances of the agents by testing them against each other in 100 games. I assigned `1` for a win, `0.5` for a tie, and `0` for a loss by player 1. 
This scoring system led to the following average scores (player 1 denoted on the rows, and player 2 denoted on the columns):

| Agent (1 \ 2) | Random | Minimax | DQN |
| :-: | :-: | :-: | :-: |
| Random | 0.520 | 0.000 | 0.455 |
| Minimax | 1.000 | 1.000 | 1.000 |
| DQN | 0.625 | 0.000 | 1.000 |

The minimax agent far surpassed the other agents, winning almost every single game. The DQN agent performed surprisingly poorly.
Although the model was trained on 51200 SARSA (state, action, reward, next state, next action) samples, given that there exist 19683 unique board states in regular tic-tac-toe, 
the network may need a larger sample size or increased depth to consistently beat a random player. 
Clever uses of rotations and reflections to augment the model may yield vast improvements to the DQN agent.
Additionally, decaying epsilon to shift model training from exploration to exploitation during training could refine the model.

## Todo
* Improve performance of the DQN agent
* Enable flexible adjustment of the GUI window (without breaking the mouse interaction)
