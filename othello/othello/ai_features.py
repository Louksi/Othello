# pylint: disable=locally-disabled, multiple-statements, line-too-long, import-error, no-name-in-module

import random
from copy import deepcopy

from othello.othello_board import OthelloBoard, Color


def get_player_at(board: OthelloBoard, x: int, y: int) -> Color:
    """Helper function to determine which player occupies a given board position."""
    if board.black.get(x, y):
        return Color.BLACK
    if board.white.get(x, y):
        return Color.WHITE
    return Color.EMPTY


def minimax(board: OthelloBoard, depth: int, max_player: Color, heuristic) -> int:
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
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """

    if depth == 0 or board.is_game_over():
        return heuristic(board, max_player)

    valid_moves = board.line_cap_move(board.current_player).hot_bits_coordinates()

    if valid_moves == []:
        return minimax(board, depth - 1, max_player, heuristic)

    if max_player == board.current_player:
        eval = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = minimax(board, depth - 1, max_player, heuristic)
            eval = max(eval, eval_score)
            board.pop()
    else:
        eval = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = minimax(board, depth - 1, max_player, heuristic)
            eval = min(eval, eval_score)
            board.pop()

    return eval


def alphabeta(
    board: OthelloBoard, depth: int, alpha: int, beta: int, max_player: Color, heuristic
) -> int:
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
    :return: The heuristic value of the best move found from the current board state.
    :rtype: int
    """

    if depth == 0 or board.is_game_over():
        return heuristic(board, max_player)

    valid_moves = board.line_cap_move(board.current_player).hot_bits_coordinates()

    if valid_moves == []:
        return minimax(board, depth - 1, max_player, heuristic)

    if max_player == board.current_player:
        eval = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = alphabeta(board, depth - 1, alpha, beta, max_player, heuristic)
            eval = max(eval, eval_score)
            board.pop()
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
    else:
        eval = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = alphabeta(board, depth - 1, alpha, beta, max_player, heuristic)
            eval = min(eval, eval_score)
            board.pop()
            beta = min(beta, eval)
            if beta <= alpha:
                break

    return eval


def create_hash():
    ZOBRIST_TABLE = [
        [[random.getrandbits(64) for _ in range(2)] for _ in range(8)] for _ in range(8)
    ]
    hash_value = 0
    for r in range(8):
        for c in range(8):
            if board[r][c] == "B":
                hash_value ^= ZOBRIST_TABLE[r][c][0]
            elif board[r][c] == "W":
                hash_value ^= ZOBRIST_TABLE[r][c][1]
    return hash_value


def find_best_move(
    board: OthelloBoard,
    depth: int = 3,
    max_player: Color = Color.BLACK,
    search_algo: str = "minimax",
    heuristic: str = "corners_captured",
) -> tuple[int, int]:
    """
    Finds the best move according to the given search algorithm.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :param depth: The maximum depth to explore in the game tree.
    :type depth: int
    :param max_player: The player for whom the best move is being calculated (BLACK or WHITE).
    :type max_player: Color
    :param search_algo: The search algorithm to use, either "minimax" or "alphabeta".
    :type search_algo: str
    :return: The coordinates of the best move found from the current board state.
    :rtype: tuple[int, int]
    """

    if depth == 0 or board.is_game_over():
        return (-1, -1)

    if heuristic == "coin_parity":
        heuristic_function = coin_parity_heuristic
    elif heuristic == "corners_captured":
        heuristic_function = corners_captured_heuristic
    elif heuristic == "mobility":
        heuristic_function = mobility_heuristic
    else:
        heuristic_function = all_in_one_heuristic

    valid_moves = board.line_cap_move(board.current_player).hot_bits_coordinates()

    best_move = (-1, -1)
    best_score = float("-inf") if max_player == board.current_player else float("inf")
    for move_x, move_y in valid_moves:

        new_board = deepcopy(board)

        new_board.play(move_x, move_y)
        if search_algo == "minimax":
            score = minimax(new_board, depth - 1, max_player, heuristic_function)
        else:
            score = alphabeta(
                new_board,
                depth - 1,
                float("-inf"),
                float("inf"),
                max_player,
                heuristic_function,
            )

        if score > best_score:
            best_score = score
            best_move = (move_x, move_y)

    return best_move


def random_move(board: OthelloBoard) -> tuple[int, int]:
    """
    Selects a random valid move from the current board state.

    :param board: The current state of the Othello board.
    :type board: OthelloBoard
    :returns: The coordinates of a random valid move.
    :rtype: tuple[int, int]
    """

    valid_moves = board.line_cap_move(board.current_player).hot_bits_coordinates()

    return random.choice(valid_moves)


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
        (0, 0),
        (board.size.value - 1, 0),
        (0, board.size.value - 1),
        (board.size.value - 1, board.size.value - 1),
    ]

    max_corners = sum(1 for x, y in corners if get_player_at(board, x, y) == max_player)
    min_corners = sum(
        1 for x, y in corners if get_player_at(board, x, y) == ~max_player
    )

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
        return int(100 * (black_count - white_count) / (black_count + white_count))
    if max_player == Color.WHITE:
        return int(100 * (white_count - black_count) / (white_count + black_count))
    return Color.EMPTY


def mobility_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Computes the Mobility heuristic.

    A high score means the max_player has more possible moves, while a low (negative)
    score means the opponent has more.

    :param board: The Othello board instance.
    :type board: OthelloBoard
    :param max_player: The player for whom we calculate the heuristic (BLACK or WHITE).
    :type max_player: Color
    :returns: A heuristic value between -100 and 100.
    :rtype: int
    """
    black_move_count = board.line_cap_move(board.black).popcount()
    white_move_count = board.line_cap_move(board.white).popcount()

    if (black_move_count + white_move_count) != 0:
        if max_player == Color.BLACK:
            return int(
                100
                * (black_move_count - white_move_count)
                / (black_move_count + white_move_count)
            )
        if max_player == Color.WHITE:
            return int(
                100
                * (white_move_count - black_move_count)
                / (white_move_count + black_move_count)
            )
        return Color.EMPTY
    return 0


def all_in_one_heuristic(board: OthelloBoard, max_player: Color) -> int:
    w_corners = 10
    w_mobility = 4
    w_coins = 1

    return (
        w_corners * corners_captured_heuristic(board, max_player)
        + w_mobility * mobility_heuristic(board, max_player)
        + w_coins * coin_parity_heuristic(board, max_player)
    )
