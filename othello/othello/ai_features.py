import sys
import othello.parser as parser
from othello.othello_board import BoardSize, OthelloBoard, Color, GameOverException


def minimax(board: OthelloBoard, depth: int, max_player: Color, maximizing: bool) -> int:
    """
    Implements the minimax algorithm to evaluate the best possible move for a given board state.

    This function recursively explores possible moves up to a given depth, evaluating each position
    using the Corners Captured heuristic when the maximum depth is reached or the game is over.
    It returns the heuristic value of the best possible move for the given player.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth to explore in the game tree.
    :type depth: int
    :param max_player: The player for whom the best move is being calculated (BLACK or WHITE).
    :type max_player: Color
    :param maximizing: A Boolean indicating whether the current step is maximizing or minimizing the score.
    :type maximizing: bool
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """

    try:
        if depth == 0:
            return corners_captured_heuristic(board, max_player)

        eval = float("-inf") if maximizing else float("inf")
        for move_x in range(board.size.value):
            for move_y in range(board.size.value):
                if board.line_cap_move(board.current_player).get(move_x, move_y):
                    print(board.export())
                    try:
                        # Need a copy, problem for future us
                        board.play(move_x, move_y)
                    except GameOverException:
                        return corners_captured_heuristic(board, max_player)

                    eval_score = minimax(
                        board, depth - 1, max_player, not maximizing)
                    if maximizing:
                        eval = max(eval, eval_score)
                    else:
                        eval = min(eval, eval_score)

        return eval

    except GameOverException:
        return corners_captured_heuristic(board, max_player)


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
