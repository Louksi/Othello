from random import choice

from othello.othello_board import BoardSize, Color, OthelloBoard


class RandomPlayerAbstraction(OthelloBoard):
    def __init__(self, size: BoardSize, random_player_color: Color):
        self._random_player_color = random_player_color
        super().__init__(size)

    def ready(self):
        if self._random_player_color is Color.BLACK:
            self._play()

    def _play(self):
        move = choice(self.line_cap_move(
            self._random_player_color).hot_bits_coordinates())
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        super().play(x_coord, y_coord)
        if self.current_player == self._random_player_color:
            self._play()
