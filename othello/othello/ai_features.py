import sys
import othello.parser as parser
from othello.othello_board import BoardSize, OthelloBoard, Color


def corners_captured_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Computes the Corners Captured heuristic.

    A high score means the max_player has more corners, while a low (negative) score means the opponent has more.

    :param board: The Othello board instance.
    :type board: OthelloBoard
    :param max_player: The player for whom we calculate the heuristic (BLACK or WHITE).
    :type max_player: Color
    :returns: A heuristic value between -100 and 100.
    :rtype: int
    """
    corners = [
        (0, 0), (board.size.value - 1, 0),
        (0, board.size.value - 1), (board.size.value - 1, board.size.value - 1)
    ]

    def get_player_at(x: int, y: int) -> Color:
        """Helper function to determine which player occupies a given board position."""
        if board.black.get(x, y):
            return Color.BLACK
        elif board.white.get(x, y):
            return Color.WHITE
        return Color.EMPTY

    max_corners = sum(
        1 for x, y in corners if get_player_at(x, y) == max_player)
    min_corners = sum(
        1 for x, y in corners if get_player_at(x, y) == ~max_player)

    if (max_corners + min_corners != 0):
        return int(100 * (max_corners - min_corners) / (max_corners + min_corners))
    return 0
