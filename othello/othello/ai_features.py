# pylint: disable=locally-disabled, multiple-statements, line-too-long, import-error, no-name-in-module

import random
import time
from copy import deepcopy
from typing import Dict, Optional, Tuple

from othello.othello_board import OthelloBoard, Color


def get_player_at(board: OthelloBoard, x: int, y: int) -> Color:
    """Helper function to determine which player occupies a given board position."""
    if board.black.get(x, y):
        return Color.BLACK
    if board.white.get(x, y):
        return Color.WHITE
    return Color.EMPTY


def create_zobrist_table():
    """
    Create a Zobrist hashing table with random 64-bit integers for board positions.

    :return: A 3D list representing Zobrist hash values for each board position and color.
    :rtype: List[List[List[int]]]
    """
    return [[[random.getrandbits(64) for _ in range(2)] for _ in range(8)] for _ in range(8)]


def compute_board_hash(board: OthelloBoard, zobrist_table: list[list[list[int]]]) -> int:
    """
    Compute the Zobrist hash for the current board state.

    :param board: The current Othello board.
    :type board: OthelloBoard
    :param zobrist_table: Pre-generated Zobrist hashing table.
    :type zobrist_table: List[List[List[int]]]
    :return: A 64-bit hash value representing the board state.
    :rtype: int
    """
    hash_value = 0
    for x in range(board.size.value):
        for y in range(board.size.value):
            if get_player_at(board, x, y) == Color.BLACK:
                hash_value ^= zobrist_table[x][y][0]
            elif get_player_at(board, x, y) == Color.WHITE:
                hash_value ^= zobrist_table[x][y][1]
    return hash_value


def move_hash(board: OthelloBoard, board_hash: int, zobrist_table: list[list[list[int]]],
              x: int, y: int, color: Color) -> int:
    """
    Update the Zobrist hash when a move is made.

    :param board_hash: Current board hash.
    :type board_hash: int
    :param zobrist_table: Zobrist hashing table.
    :type zobrist_table: List[List[List[int]]]
    :param x: X-coordinate of the move.
    :type x: int
    :param y: Y-coordinate of the move.
    :type y: int
    :param color: Color of the player making the move.
    :type color: Color
    :return: Updated board hash after the move.
    :rtype: int
    """
    board_hash ^= zobrist_table[x][y][0 if color == Color.BLACK else 1]

    captured_pieces = board.line_cap(x, y, color)
    captured_coords = captured_pieces.hot_bits_coordinates()

    opposite_color = Color.WHITE if color == Color.BLACK else Color.BLACK

    for cap_x, cap_y in captured_coords:
        board_hash ^= zobrist_table[cap_x][cap_y][0 if opposite_color ==
                                                  Color.BLACK else 1]
        board_hash ^= zobrist_table[cap_x][cap_y][0 if color ==
                                                  Color.BLACK else 1]

    return board_hash


class TranspositionTable:
    """
    Transposition table to store and retrieve board states and their evaluations.
    """

    def __init__(self, max_size: int = 1_000_000):
        """
        Initialize the transposition table.

        :param max_size: Maximum number of entries to store.
        :type max_size: int
        """
        self.table: Dict[int, Tuple[int, int]] = {}
        self.max_size = max_size

    def store(self, board_hash: int, depth: int, score: int):
        """
        Store a board state in the transposition table.

        :param board_hash: Zobrist hash of the board state.
        :type board_hash: int
        :param depth: Depth of the search.
        :type depth: int
        :param score: Evaluation score of the board state.
        :type score: int
        """
        if len(self.table) >= self.max_size:
            # Remove the least valuable entry if table is full
            self.table.pop(min(self.table, key=lambda k: self.table[k][1]))

        self.table[board_hash] = (score, depth)

    def lookup(self, board_hash: int, depth: int) -> Optional[int]:
        """
        Retrieve a stored board state score if available.

        :param board_hash: Zobrist hash of the board state.
        :type board_hash: int
        :param depth: Current search depth.
        :type depth: int
        :return: Stored score if found and depth is sufficient, otherwise None.
        :rtype: Optional[int]
        """
        entry = self.table.get(board_hash)
        if entry and entry[1] >= depth:
            return entry[0]
        return None


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

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

    if valid_moves == []:
        return minimax(board, depth - 1, max_player, heuristic)

    if max_player == board.current_player:
        eval = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = minimax(
                board, depth - 1, max_player, heuristic)
            eval = max(eval, eval_score)
            board.pop()
    else:
        eval = float("inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = minimax(
                board, depth - 1, max_player, heuristic)
            eval = min(eval, eval_score)
            board.pop()

    return eval


def alphabeta(board: OthelloBoard, depth: int, alpha: int,
              beta: int, max_player: Color, heuristic) -> int:
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

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

    if valid_moves == []:
        return alphabeta(board, depth - 1, alpha, beta, max_player, heuristic)

    if max_player == board.current_player:
        eval = float("-inf")
        for move_x, move_y in valid_moves:
            board.play(move_x, move_y)
            eval_score = alphabeta(
                board, depth - 1, alpha, beta, max_player, heuristic)
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
                board, depth - 1, alpha, beta, max_player, heuristic)
            eval = min(eval, eval_score)
            board.pop()
            beta = min(beta, eval)
            if beta <= alpha:
                break

    return eval


def find_best_move(board: OthelloBoard, depth: int = 3, max_player: Color = Color.BLACK, search_algo: str = "minimax", heuristic: str = "corners_captured") -> tuple[int, int]:
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

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

    best_move = (-1, -1)
    best_score = float(
        "-inf") if max_player == board.current_player else float("inf")
    for move_x, move_y in valid_moves:

        new_board = deepcopy(board)

        new_board.play(move_x, move_y)
        if search_algo == "minimax":
            score = minimax(new_board, depth - 1,
                            max_player, heuristic_function)
        else:
            score = alphabeta(
                new_board, depth - 1, float("-inf"), float("inf"),
                max_player, heuristic_function)

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

    valid_moves = board.line_cap_move(
        board.current_player).hot_bits_coordinates()

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
        (0, 0), (board.size.value - 1, 0),
        (0, board.size.value - 1), (board.size.value - 1, board.size.value - 1)
    ]

    max_corners = sum(
        1 for x, y in corners if get_player_at(board, x, y) == max_player)
    min_corners = sum(
        1 for x, y in corners if get_player_at(board, x, y) == ~max_player)

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
            return int(100 * (black_move_count - white_move_count) /
                       (black_move_count + white_move_count))
        if max_player == Color.WHITE:
            return int(100 * (white_move_count - black_move_count) /
                       (white_move_count + black_move_count))
        return Color.EMPTY
    return 0


def all_in_one_heuristic(board: OthelloBoard, max_player: Color) -> int:
    """
    Computes the All-in-One heuristic.

    This heuristic is a weighted sum of the Corners Captured, Mobility, and Coin Parity
    heuristics. The weights are chosen such that capturing corners is the most important
    aspect of the game, followed by controlling the number of possible moves (mobility),
    and then by controlling the number of coins (parity).

    :param board: The Othello board instance.
    :type board: OthelloBoard
    :param max_player: The player for whom we calculate the heuristic (BLACK or WHITE).
    :type max_player: Color
    :returns: A heuristic value between -100 and 100.
    :rtype: int
    """
    w_corners = 10
    w_mobility = 4
    w_coins = 1

    return (w_corners * corners_captured_heuristic(board, max_player) +
            w_mobility * mobility_heuristic(board, max_player) +
            w_coins * coin_parity_heuristic(board, max_player))
