import pytest
from othello.othello_board import OthelloBoard, BoardSize, Color, GameOverException
from othello.ai_features import corners_captured_heuristic, coin_parity_heuristic, find_best_move, minimax

# region Fixtures


@pytest.fixture
def empty_board():
    """Creates an empty Othello board."""
    return OthelloBoard(BoardSize.EIGHT_BY_EIGHT)


@pytest.fixture
def board_with_corners():
    """Creates an Othello board where BLACK has 2 corners and WHITE has 1."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.black.set(7, 7, True)
    board.white.set(7, 0, True)
    return board


@pytest.fixture
def board_with_all_corners():
    """Creates an Othello board where BLACK has all four corners."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.black.set(7, 0, True)
    board.black.set(0, 7, True)
    board.black.set(7, 7, True)
    return board


@pytest.fixture
def board_one_corner_each():
    """Creates an Othello board where BLACK has 1 corner and WHITE has 1 corner."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.white.set(7, 7, True)
    return board


@pytest.fixture
def board_6_one_move_possible():
    """Creates an Othello board where WHITE only have 1 possible move."""
    board = OthelloBoard(BoardSize.SIX_BY_SIX)
    board.current_player = Color.WHITE
    board.black.set(0, 4, True)
    board.black.set(0, 5, True)
    board.black.set(1, 4, True)
    board.black.set(1, 5, True)
    board.black.set(2, 4, True)
    board.black.set(2, 5, True)
    board.black.set(3, 4, True)
    board.black.set(3, 5, True)
    board.black.set(4, 4, True)
    board.black.set(4, 5, True)
    board.white.set(1, 1, True)
    board.white.set(1, 2, True)
    board.white.set(1, 3, True)
    board.white.set(2, 2, True)
    board.white.set(2, 3, True)
    board.white.set(3, 2, True)
    board.white.set(3, 3, True)
    board.white.set(4, 2, True)
    return board

# endregion Fixtures

# region Corners Captured


def test_empty_board_corners(empty_board):
    """Tests that an empty board gives a score of 0 for both players."""
    assert corners_captured_heuristic(empty_board, Color.BLACK) == 0
    assert corners_captured_heuristic(empty_board, Color.WHITE) == 0


def test_corners_advantage_black(board_with_corners):
    """Tests that BLACK gets a positive score when having more corners than WHITE."""
    assert corners_captured_heuristic(board_with_corners, Color.BLACK) > 0
    assert corners_captured_heuristic(board_with_corners, Color.WHITE) < 0


def test_all_corners_black(board_with_all_corners):
    """Tests that BLACK gets the maximum score when owning all corners."""
    assert corners_captured_heuristic(
        board_with_all_corners, Color.BLACK) == 100
    assert corners_captured_heuristic(
        board_with_all_corners, Color.WHITE) == -100


def test_one_corner_each(board_one_corner_each):
    """Tests that if both players have the same number of corners, the score is 0."""
    assert corners_captured_heuristic(board_one_corner_each, Color.BLACK) == 0
    assert corners_captured_heuristic(board_one_corner_each, Color.WHITE) == 0

# endregion Corners Captured

# region Coin Parity


def test_empty_board_coin_parity(empty_board):
    """Tests that an empty board gives a score of 0 for both players."""
    assert coin_parity_heuristic(empty_board, Color.BLACK) == 0
    assert coin_parity_heuristic(empty_board, Color.WHITE) == 0


def test_coin_parity_advantage_black(board_with_corners):
    """Tests that BLACK gets a positive score when having more coins than WHITE."""
    assert coin_parity_heuristic(board_with_corners, Color.BLACK) > 0
    assert coin_parity_heuristic(board_with_corners, Color.WHITE) < 0


def test_coin_parity_advantage_white(board_one_corner_each):
    """Tests that WHITE gets a negative score when having more coins than BLACK."""
    board_one_corner_each.white.set(1, 1, True)
    assert coin_parity_heuristic(board_one_corner_each, Color.BLACK) < 0
    assert coin_parity_heuristic(board_one_corner_each, Color.WHITE) > 0


def test_draw_coin_parity(board_one_corner_each):
    """Tests that if both players have the same number of coins, the score is 0."""
    assert coin_parity_heuristic(board_one_corner_each, Color.BLACK) == 0
    assert coin_parity_heuristic(board_one_corner_each, Color.WHITE) == 0


def test_invalid_color_empty_coin_parity(empty_board):
    """Tests that the function returns Color.EMPTY when no color is given. (invalid color)"""
    assert coin_parity_heuristic(empty_board, Color.EMPTY) == Color.EMPTY

# endregion Coin Parity

# region Find Best Move


def test_1_move_possible(board_6_one_move_possible):
    """Tests that the function returns the only possible move."""
    print(board_6_one_move_possible.export_board())
    print(find_best_move(board_6_one_move_possible, 1, Color.WHITE, True, "minimax"))
    print(find_best_move(board_6_one_move_possible,
          1, Color.WHITE, True, "alphabeta"))
    assert find_best_move(board_6_one_move_possible, 1,
                          Color.WHITE, True, "minimax") == (1, 1)
    assert find_best_move(board_6_one_move_possible, 1,
                          Color.WHITE, True, "alphabeta") == (1, 1)

# endregion Find Best Move
