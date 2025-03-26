from random import choice

from othello.ai_features import find_best_move
from othello.othello_board import BoardSize, Color, OthelloBoard
from othello.parser import AIColor


class GameController():
    def __init__(self, board: OthelloBoard):
        self._board = board
        self.size = board.size
        self.first_player_human = True
        self.post_play_callback = None
        self.is_blitz = False

    def ready(self):
        pass

    def play(self, x_coord: int, y_coord: int):
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()

    def get_possible_moves(self, player: Color):
        return self._board.line_cap_move(player)

    def get_position(self, player: Color, x_coord: int, y_coord: int):
        to_query = self._board.black if player is Color.BLACK else self._board.white
        return to_query.get(x_coord, y_coord)

    def restart(self):
        self._board.restart()

    def is_game_over(self):
        return self._board.is_game_over()

    def get_current_player(self):
        return self._board.current_player

    def get_pieces_count(self, player_color: Color):
        return self._board.black.popcount() if player_color is Color.BLACK \
            else self._board.white.popcount()

    def export(self):
        return self._board.export()

    def export_history(self):
        return self._board.export_history()

    def __str__(self):
        return str(self._board)


class RandomPlayerGameController(GameController):
    def __init__(self, board: OthelloBoard, random_player_color: Color):
        super().__init__(board)
        self._random_player_color = random_player_color
        self.first_player_human = random_player_color is not Color.BLACK

    def ready(self):
        if self._random_player_color is Color.BLACK:
            self._play()

    def _play(self):
        move = choice(self.get_possible_moves(
            self._random_player_color).hot_bits_coordinates())
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()
        if self._board.current_player is self._random_player_color:
            self._play()


class AIPlayerGameController(GameController):
    def __init__(self, board: OthelloBoard, ai_color: Color = Color.BLACK, depth: int = 3,
                 algorithm: str = "minimax", heuristic: str = "coin_parity", random_player: bool = False):

        super().__init__(board)

        if isinstance(ai_color, str):
            if ai_color == 'X':
                self.ai_color = Color.BLACK
            elif ai_color == 'O':
                self.ai_color = Color.WHITE
            else:
                self.ai_color = ai_color
        elif not isinstance(ai_color, Color):
            raise ValueError(
                f"Invalid ai_color type: {type(ai_color)}. Must be a string or Color enum.")

        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.random_player = random_player

    def ready(self):
        if self.ai_color is self._board.current_player:
            self._play()

    def _play(self):
        move = find_best_move(
            self._board, self.depth, self.ai_color, self.algorithm, self.heuristic)
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()
        if self._board.current_player is self.ai_color:
            self._play()
