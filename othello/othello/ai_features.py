from othello.othello_board import OthelloBoard, Color
from copy import deepcopy


def minimax(board: OthelloBoard, depth: int, max_player: Color, maximizing: bool, heuristic) -> int:
    """
    Implements the minimax algorithm to evaluate the best possible move for a given board state.

    This function recursively explores possible moves up to a given depth, evaluating each position
    using an heuristic when the maximum depth is reached or the game is over.
    It returns the heuristic value of the best possible move for the given player.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth to explore in the game tree.
    :type depth: int
    :param max_player: The player for whom the best move is being calculated (BLACK or WHITE).
    :type max_player: Color
    :param maximizing: A Boolean indicating whether the current step is maximizing or minimizing
    the score.
    :type maximizing: bool
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """

    if depth == 0 or board.is_game_over():
        return heuristic(board, max_player)

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

    if valid_moves == []:
        return minimax(board, depth - 1, max_player, not maximizing, heuristic)

    if maximizing:
        eval = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = minimax(
                board, depth - 1, max_player, not maximizing, heuristic)
            eval = max(eval, eval_score)
            board.pop()
    else:
        eval = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = minimax(
                board, depth - 1, max_player, not maximizing, heuristic)
            eval = min(eval, eval_score)
            board.pop()

    return eval


def alphabeta(board: OthelloBoard, depth: int, alpha: int,
              beta: int, max_player: Color, maximizing: bool, heuristic) -> int:
    """
    Implements the Alpha-Beta Pruning algorithm to evaluate the best possible move for a given
    board state.

    This function recursively explores possible moves up to a given depth, evaluating each position
    using an heuristic when the maximum depth is reached or the game is over.
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
    :param maximizing: A Boolean indicating whether the current step is maximizing or minimizing
    the score.
    :type maximizing: bool
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """

    if depth == 0 or board.is_game_over():
        return heuristic(board, max_player)

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

    if valid_moves == []:
        return minimax(board, depth - 1, max_player, not maximizing, heuristic)

    if maximizing:
        eval = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = alphabeta(
                board, depth - 1, alpha, beta, max_player, not maximizing, heuristic)
            eval = max(eval, eval_score)
            board.pop()
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
    else:
        eval = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = alphabeta(
                board, depth - 1, alpha, beta, max_player, not maximizing, heuristic)
            eval = min(eval, eval_score)
            board.pop()
            beta = min(beta, eval)
            if beta <= alpha:
                break

    return eval


def find_best_move(board: OthelloBoard, depth: int = 3, max_player: Color = Color.BLACK,
                   maximizing: bool = True, search_algo: str = "minimax", heuristic: str = "corners_captured") -> tuple[int, int]:
    """
    Finds the best move according to the given search algorithm.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth to explore in the game tree.
    :type depth: int
    :param max_player: The player for whom the best move is being calculated (BLACK or WHITE).
    :type max_player: Color
    :param maximizing: A Boolean indicating whether the current step is maximizing or minimizing
    the score.
    :type maximizing: bool
    :param search_algo: The search algorithm to use, either "minimax" or "alphabeta".
    :type search_algo: str
    :return: The coordinates of the best move found from the current board state.
    :rtype: tuple[int, int]
    """

    if depth == 0 or board.is_game_over():
        return (-1, -1)

    if heuristic == "coin_parity":
        heuristic_function = coin_parity_heuristic
    else:
        heuristic_function = corners_captured_heuristic

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

    best_move = (-1, -1)
    best_score = float("-inf") if maximizing else float("inf")
    for move_x, move_y in valid_moves:

        new_board = deepcopy(board)

        new_board.play(move_x, move_y)
        if search_algo == "minimax":
            score = minimax(new_board, depth - 1,
                            max_player, not maximizing, heuristic_function)
        else:
            score = alphabeta(
                new_board, depth - 1, float("-inf"), float("inf"),
                max_player, not maximizing, heuristic_function)

        if score > best_score:
            best_score = score
            best_move = (move_x, move_y)

    return best_move


def corners_captured_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Computes the Corners Captured heuristic.

    A high score means the max_player has more corners, while a low (negative) score means the
    opponent has more.

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
        if board.white.get(x, y):
            return Color.WHITE
        return Color.EMPTY

    max_corners = sum(
        1 for x, y in corners if get_player_at(x, y) == max_player)
    min_corners = sum(
        1 for x, y in corners if get_player_at(x, y) == ~max_player)

    if max_corners + min_corners != 0:
        return int(100 * (max_corners - min_corners) / (max_corners + min_corners))
    return 0


def coin_parity_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Computes the Coin Parity heuristic.

    A high score means the max_player has more pieces on the board, while a low (negative)
    score means the opponent has more.

    :param board: The Othello board instance.
    :type board: OthelloBoard
    :param max_player: The player for whom we calculate the heuristic (BLACK or WHITE).
    :type max_player: Color
    :returns: A heuristic value between -100 and 100.
    :rtype: int
    """

    black_count = board.black.popcount()
    white_count = board.white.popcount()

    if max_player == Color.BLACK:
        return int(100 * (black_count - white_count) /
                   (black_count + white_count))
    if max_player == Color.WHITE:
        return int(100 * (white_count - black_count) /
                   (white_count + black_count))
    return Color.EMPTY

# def mobility_heuristic(board: OthelloBoard, max_player: Color) -> int:

#     black_move_count = board.line_cap_move(board.current_player).popcount()
