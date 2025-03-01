import sys
import othello.parser as parser
from othello.othello_board import BoardSize, OthelloBoard, Color, GameOverException
from othello.bitboard import Bitboard


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

    if depth == 0 or board.is_game_over():
        return corners_captured_heuristic(board, max_player)

    if maximizing:
        eval = float("-inf")
        for move_x in range(board.size.value):
            for move_y in range(board.size.value):
                if board.line_cap_move(board.current_player).get(move_x, move_y):
                    # Need a copy, problem for future us
                    board.play(move_x, move_y)
                    eval_score = minimax(
                        board, depth - 1, max_player, not maximizing)
                    eval = max(eval, eval_score)
                    board.pop()
    else:
        eval = float("inf")
        for move_x in range(board.size.value):
            for move_y in range(board.size.value):
                if board.line_cap_move(board.current_player).get(move_x, move_y):
                    # Need a copy, problem for future us
                    board.play(move_x, move_y)
                    eval_score = minimax(
                        board, depth - 1, max_player, maximizing)
                    eval = min(eval, eval_score)
                    board.pop()

    return eval


def alphabeta(board: OthelloBoard, depth: int, alpha: int, beta: int, max_player: Color, maximizing: bool) -> int:
    """
    Implements the Alpha-Beta Pruning algorithm to evaluate the best possible move for a given board state.

    This function recursively explores possible moves up to a given depth, evaluating each position
    using the Corners Captured heuristic when the maximum depth is reached or the game is over.
    It returns the heuristic value of the best move found from the current board state.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth to explore in the game tree.
    :type depth: int
    :param alpha: The best possible score for the maximizing player.
    :type alpha: int
    :param beta: The best possible score for the minimizing player.
    :type beta: int
    :param max_player: The player for whom the best move is being calculated (BLACK or WHITE).
    :type max_player: Color
    :param maximizing: A Boolean indicating whether the current step is maximizing or minimizing the score.
    :type maximizing: bool
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """

    if depth == 0 or board.is_game_over():
        return corners_captured_heuristic(board, max_player)

    if maximizing:
        eval = float("-inf")
        for move_x in range(board.size.value):
            for move_y in range(board.size.value):
                if board.line_cap_move(board.current_player).get(move_x, move_y):
                    # Need a copy, problem for future us
                    board.play(move_x, move_y)
                    eval_score = alphabeta(
                        board, depth - 1, alpha, beta, max_player, not maximizing)
                    eval = max(eval, eval_score)
                    board.pop()
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
    else:
        eval = float("inf")
        for move_x in range(board.size.value):
            for move_y in range(board.size.value):
                if board.line_cap_move(board.current_player).get(move_x, move_y):
                    # Need a copy, problem for future us
                    board.play(move_x, move_y)
                    eval_score = alphabeta(
                        board, depth - 1, alpha, beta, max_player, maximizing)
                    eval = min(eval, eval_score)
                    board.pop()
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break

    return eval


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


def coin_parity_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Computes the Coin Parity heuristic.

    A high score means the max_player has more pieces on the board, while a low (negative) score means the opponent has more.

    :param board: The Othello board instance.
    :type board: OthelloBoard
    :param max_player: The player for whom we calculate the heuristic (BLACK or WHITE).
    :type max_player: Color
    :returns: A heuristic value between -100 and 100.
    :rtype: int
    """

    if max_player == Color.BLACK:
        return int(100 * (board.black.popcount() - board.white.popcount())/(board.black.popcount() + board.white.popcount()))
    if max_player == Color.WHITE:
        return int(100 * (board.white.popcount() - board.black.popcount())/(board.white.popcount() + board.black.popcount()))
