import pytest
from othello.othello_board import OthelloBoard, BoardSize, Color, GameOverException
from othello.ai_features import corners_captured_heuristic, minimax


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


def test_one_corner_each():
    """Tests that if both players have the same number of corners, the score is 0."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.white.set(7, 7, True)
    assert corners_captured_heuristic(board, Color.BLACK) == 0
    assert corners_captured_heuristic(board, Color.WHITE) == 0


@pytest.fixture
def board_game_over():
    """Creates an Othello board with no available moves (game over)."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.current_player = Color.BLACK
    return board


def test_minimax_depth_limit(board_with_corners):
    """Tests that minimax returns the correct heuristic at depth 0."""
    result = minimax(board_with_corners, depth=0,
                     max_player=Color.BLACK, maximizing=True)
    assert result == corners_captured_heuristic(
        board_with_corners, Color.BLACK)


def test_minimax_game_over(board_game_over):
    """Tests that minimax evaluates the board correctly when there are no legal moves."""
    result = minimax(board_game_over, depth=3,
                     max_player=Color.BLACK, maximizing=True)
    assert result == corners_captured_heuristic(board_game_over, Color.BLACK)


def test_minimax_maximizing_player(board_with_corners):
    """Tests that minimax maximizes correctly for a player with more corners."""
    result = minimax(board_with_corners, depth=3,
                     max_player=Color.BLACK, maximizing=True)
    assert result > 0


def test_minimax_minimizing_player(board_with_corners):
    """Tests that minimax minimizes correctly for a player with fewer corners."""
    result = minimax(board_with_corners, depth=3,
                     max_player=Color.WHITE, maximizing=False)
    assert result < 0


def test_minimax_equal_corners():
    """Tests that minimax returns a score of 0 when both players have the same number of corners."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    board.black.set(0, 0, True)
    board.white.set(7, 7, True)
    result_black = minimax(
        board, depth=3, max_player=Color.BLACK, maximizing=True)
    result_white = minimax(
        board, depth=3, max_player=Color.WHITE, maximizing=False)
    assert result_black == 0
    assert result_white == 0
