from random import choice

from othello.othello_board import BoardSize, Color, OthelloBoard

class PlayerAbstraction():
    def __init__(self, board: OthelloBoard):
        self._board = board
        self.size = board.size
        self.first_player_human = True
        self.post_play_callback = None

    def ready(self):
        pass

    def play(self, x_coord: int, y_coord: int):
        self._board.play(x_coord, y_coord)

    def line_cap_move(self, player: Color):
        return self._board.line_cap_move(player)

    def restart(self):
        self._board.restart()

    def is_game_over(self):
        return self._board.is_game_over()

    def get_current_player(self):
        return self._board.current_player

    def get_possible_moves(self):
        return self._board.line_cap_move(self._board.current_player)

    def __str__(self):
        return str(self._board)

class RandomPlayerAbstraction(PlayerAbstraction):
    def __init__(self, board: OthelloBoard, random_player_color: Color):
        super().__init__(board)
        self._random_player_color = random_player_color
        self.first_player_human = random_player_color is not Color.BLACK

    def ready(self):
        if self._random_player_color is Color.BLACK:
            self._play()

    def _play(self):
        move = choice(self.line_cap_move(
            self._random_player_color).hot_bits_coordinates())
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()
        if self._board.current_player is self._random_player_color:
            self._play()
