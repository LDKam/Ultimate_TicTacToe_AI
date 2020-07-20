import sys
import time
from collections import defaultdict

from PySide2.QtCore import QPointF, QRectF, Qt
from PySide2.QtGui import QColor, QPen
from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem

from game import *
from main import process_args
from util import is_curr_player_human


class UltimateTicTacToeView(QGraphicsView):
    def __init__(self, player_1: Player, player_2: Player, size: int = 600):
        super().__init__()
        self.setWindowTitle("Ultimate Tic-Tac-Toe")
        self.player_1 = player_1
        self.player_2 = player_2
        self.game = UltimateTicTacToe()
        self.size = size  # size of window
        self.maxi_size = size
        self.mini_size = int(self.size / 3 * 0.8)
        self.click_needed = False
        self.clear = True

        scene = QGraphicsScene()
        self.board = TicTacToeBoard(state=self.game.get_maxiboard(),
                                    point=(self.size // 2, self.size // 2),
                                    size=self.maxi_size,
                                    board_thickness=6,
                                    token_thickness=4)
        scene.addItem(self.board)
        self.mini_centers = self._find_miniboard_centers()
        self.miniboards = [TicTacToeBoard(state=self.game.get_miniboard(i),
                                          point=self.mini_centers[i],
                                          size=self.mini_size,
                                          board_thickness=3,
                                          token_thickness=8)
                           for i in range(9)]
        for miniboard in self.miniboards:
            scene.addItem(miniboard)
            miniboard.setPos(miniboard.get_point()[0], miniboard.get_point()[1])
        scene.setSceneRect(0, 0, self.size, self.size)
        self.setScene(scene)

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == Qt.Key_S:  # start the game
            self.run_game()
        if key == Qt.Key_R:  # reset the game
            self.reset()

    def run_game(self) -> None:
        """Progress through game, updating the GUI to display the results of each turn.
        Defers to a mouse press event for human input.
        """
        self.clear = False
        while not self.game.is_game_over() and not is_curr_player_human(self.game, self.player_1, self.player_2):
            start_time = time.time()
            self.highlight_valid_moves()
            if self.game.get_curr_player() == 1:
                move = self.player_1.choose_move(self.game)
            else:
                move = self.player_2.choose_move(self.game)
            if self.clear:
                return
            delta_time = 1 - (time.time() - start_time)
            if delta_time > 0:
                time.sleep(delta_time)
            self.update_all_elements(move)
        if not self.game.is_game_over() and is_curr_player_human(self.game, self.player_1, self.player_2):
            self.highlight_valid_moves()
            self.click_needed = True
        QApplication.processEvents()

    def highlight_valid_moves(self) -> None:
        """Highlights all squares that are valid moves for the player.
        """
        valid_miniboard, valid_moves = self.game.get_valid_miniboards_and_moves()
        if valid_miniboard == -1:
            moves_dict = defaultdict(list)
            for valid_move in valid_moves:
                moves_dict[valid_move[0]].append(valid_move[1])
            for valid_miniboard in moves_dict.keys():
                color = QColor(255, 0, 0, 25) if self.game.get_curr_player() == 1 else QColor(0, 0, 255, 25)
                self.miniboards[valid_miniboard].highlight_square(moves_dict[valid_miniboard], color)
        else:
            color = QColor(255, 0, 0, 25) if self.game.get_curr_player() == 1 else QColor(0, 0, 255, 25)
            self.miniboards[valid_miniboard].highlight_square([i for _, i in valid_moves], color)
        QApplication.processEvents()

    def update_all_elements(self, move: Move) -> None:
        """Updates the game state and GUI.
        """
        self.game.update(move)
        self.miniboards[move[0]].update_item(self.game.get_miniboard(move[0]))
        self.board.update_item(self.game.get_maxiboard())
        QApplication.processEvents()

    def mousePressEvent(self, event) -> None:
        """Get a requested move if human input is needed and update the game state if the move is valid.
        """
        if not self.click_needed:
            return
        pos = event.pos()
        for mini_i in range(9):
            i = self.miniboards[mini_i].where_within_board(pos.x(), pos.y())
            if i is not None:
                move = (mini_i, i)
                _, valid_moves = self.game.get_valid_miniboards_and_moves()
                if move in valid_moves:
                    self.update_all_elements(move)
                    self.click_needed = False
                    self.run_game()
                break

    def reset(self) -> None:
        """Resets the game and clears the board for another game.
        """
        self.clear = True
        self.game.reset()
        self.board.clear_board()
        for miniboard in self.miniboards:
            miniboard.clear_board()
        QApplication.processEvents()

    def _find_miniboard_centers(self) -> List[Tuple[int, int]]:
        """Finds the center coordinates for all the miniboards.
        """
        coords = [int(self.size / 2 - self.mini_size / 2 + (i - 1) * self.maxi_size / 3) for i in range(3)]
        return [(x, y) for y in coords for x in coords]


class TicTacToeBoard(QGraphicsItem):
    def __init__(self, state: List[int], point: Tuple[int, int], size: int, board_thickness: int, token_thickness: int):
        super().__init__()
        self.state = state
        self.point = point
        self.size = size
        self.token_size = self.size // 5
        self.board_thickness = board_thickness
        self.token_thickness = token_thickness
        self.clear = False
        self.highlight = []
        self.highlight_color = Qt.lightGray

    def boundingRect(self):
        return QRectF(0, 0, self.size, self.size)

    # noinspection PyMethodOverriding
    def paint(self, painter, option, widget):
        """Draws all the components of the tic-tac-toe board.
        """
        if self.clear:
            painter.fillRect(self.boundingRect(), Qt.white)
            self.clear = False

        if self.highlight:
            for i in self.highlight:
                x = i % 3
                y = i // 3
                square = QRectF((x * self.size) // 3, (y * self.size) // 3, self.size // 3, self.size // 3)
                painter.fillRect(square, self.highlight_color)
            self.highlight = []
        self.draw_board(painter)
        for i in range(9):
            self.draw_tokens(painter, i)

    def draw_board(self, painter) -> None:
        """Draws the frame of the tic-tac-toe board.
        """
        painter.setPen(QPen(Qt.black, self.board_thickness))
        painter.drawLine(0, self.size // 3, self.size, self.size // 3)
        painter.drawLine(0, 2 * self.size // 3, self.size, 2 * self.size // 3)
        painter.drawLine(self.size // 3, 0, self.size // 3, self.size)
        painter.drawLine(2 * self.size // 3, 0, 2 * self.size // 3, self.size)

    def draw_tokens(self, painter, i: int) -> None:
        """Draws the tic-tac-toe tokens (red for player x, blue for player o) in the appropriate positions of the board.
        """
        x = i % 3
        y = i // 3
        if self.state[i] == 1:
            painter.setPen(QPen(Qt.red, self.token_thickness))
            center = (self.size // 6 + x * (self.size // 3), self.size // 6 + y * (self.size // 3))
            painter.drawLine(center[0] - self.token_size // 2, center[1] - self.token_size // 2,
                             center[0] + self.token_size // 2, center[1] + self.token_size // 2)
            painter.drawLine(center[0] - self.token_size // 2, center[1] + self.token_size // 2,
                             center[0] + self.token_size // 2, center[1] - self.token_size // 2)
        elif self.state[i] == -1:
            painter.setPen(QPen(Qt.blue, self.token_thickness))
            center = (self.size // 6 + x * (self.size // 3), self.size // 6 + y * (self.size // 3))
            painter.drawEllipse(QPointF(center[0], center[1]), self.token_size // 2, self.token_size // 2)

    def update_item(self, state: List[int]) -> None:
        """Updates the board GUI to reflect an updated game state.
        """
        self.state = state
        self.update()

    def highlight_square(self, indices: List[int], color: QColor) -> None:
        """Highlights the squares of valid moves in the desired color.
        """
        self.highlight = indices
        self.highlight_color = color
        self.update()

    def get_point(self):
        return self.point

    def where_within_board(self, x: int, y: int) -> Optional[int]:
        """Finds which square of the tic-tac-toe board the coordinate is located in.
        """
        local_x = x - self.point[0]
        local_y = y - self.point[1]
        if 0 < local_x < self.size and 0 < local_y < self.size:
            return (3 * local_x // self.size) + 3 * (3 * local_y // self.size)
        return None

    def clear_board(self) -> None:
        """Clears the board by painting a white rectangle over the contents of the board.
        """
        self.clear = True
        self.update_item([0] * 9)


if __name__ == '__main__':
    """Plays human vs. AI or AI vs. AI. Use -d to refer to a deep q-learning player, -h to refer to a human player, 
    -m to refer to a minimax bot, and -r to refer to a random bot. Press the s key to start the game. 
    Press the r key to clear the board. Click on one of the highlighted squares to play a move.
    """
    p1, p2 = process_args(sys.argv)
    app = QApplication(sys.argv)
    view = UltimateTicTacToeView(player_1=p1, player_2=p2)
    view.show()
    sys.exit(app.exec_())
