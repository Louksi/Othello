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


def test_minimax_depth_limit(board_with_corners):
    """Tests that minimax returns the correct heuristic at depth 0."""
    result = minimax(board_with_corners, depth=0,
                     max_player=Color.BLACK, maximizing=True)
    assert result == corners_captured_heuristic(
        board_with_corners, Color.BLACK)


@pytest.fixture
def standard_board():
    """Creates a standard Othello starting position."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    # Standard starting position with 4 center pieces
    board.black.set(3, 4, True)
    board.black.set(4, 3, True)
    board.white.set(3, 3, True)
    board.white.set(4, 4, True)
    board.current_player = Color.BLACK
    return board


@pytest.fixture
def almost_finished_board():
    """Creates a board with only a few moves remaining."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    # Fill most of the board with pieces
    for x in range(8):
        for y in range(8):
            # Leave only a few spaces empty
            if not ((x == 7 and y == 7) or (x == 6 and y == 7)):
                if (x + y) % 2 == 0:
                    board.black.set(x, y, True)
                else:
                    board.white.set(x, y, True)
    board.current_player = Color.BLACK
    return board


@pytest.fixture
def game_over_board():
    """Creates a board where the game is over with BLACK winning."""
    board = OthelloBoard(BoardSize.EIGHT_BY_EIGHT)
    # Fill the entire board with BLACK pieces except one corner
    for x in range(8):
        for y in range(8):
            if not (x == 7 and y == 7):
                board.black.set(x, y, True)
    # Add one WHITE piece
    board.white.set(7, 7, True)
    return board


def test_minimax_standard_position(standard_board):
    """Tests minimax on the standard starting position with various depths."""
    # Depth 1 should evaluate moves one step ahead
    result_depth_1 = minimax(standard_board, depth=1,
                             max_player=Color.BLACK, maximizing=True)

    # Depth 2 should evaluate opponent's responses
    result_depth_2 = minimax(standard_board, depth=2,
                             max_player=Color.BLACK, maximizing=True)

    # Ensure the function returns a numeric value
    assert isinstance(result_depth_1, (int, float))
    assert isinstance(result_depth_2, (int, float))


def test_minimax_opponent_perspective(standard_board):
    """Tests that minimax works when evaluating from WHITE's perspective."""
    black_perspective = minimax(
        standard_board, depth=1, max_player=Color.BLACK, maximizing=True)

    # Change current player to WHITE
    standard_board.current_player = Color.WHITE
    white_perspective = minimax(
        standard_board, depth=1, max_player=Color.WHITE, maximizing=True)

    # The values should be different since they're from different perspectives
    assert black_perspective != white_perspective


def test_minimax_almost_finished(almost_finished_board):
    """Tests minimax on a nearly complete board."""
    result = minimax(almost_finished_board, depth=3,
                     max_player=Color.BLACK, maximizing=True)

    # Ensure the function returns a value within the expected range for corners heuristic
    assert -100 <= result <= 100


def test_minimax_game_over(game_over_board):
    """Tests that minimax correctly handles game over situations."""
    # When the game is over, it should immediately return the heuristic value
    result = minimax(game_over_board, depth=5,
                     max_player=Color.BLACK, maximizing=True)
    expected = corners_captured_heuristic(game_over_board, Color.BLACK)

    assert result == expected


def test_minimax_maximizing_vs_minimizing(standard_board):
    """Tests that maximizing and minimizing modes produce different results."""
    max_result = minimax(standard_board, depth=2,
                         max_player=Color.BLACK, maximizing=True)
    min_result = minimax(standard_board, depth=2,
                         max_player=Color.BLACK, maximizing=False)

    # The results should be different
    assert max_result != min_result


def test_minimax_different_max_player(standard_board):
    """Tests minimax with different max_player values."""
    black_result = minimax(standard_board, depth=2,
                           max_player=Color.BLACK, maximizing=True)
    white_result = minimax(standard_board, depth=2,
                           max_player=Color.WHITE, maximizing=True)

    # BLACK and WHITE should get different evaluations
    assert black_result != white_result


def test_minimax_increasing_depth(standard_board):
    """Tests that increasing depth changes the evaluation."""
    results = []
    for depth in range(4):  # Test depths 0-3
        results.append(minimax(standard_board, depth=depth,
                       max_player=Color.BLACK, maximizing=True))

    # At least some of the results should be different as depth increases
    assert len(
        set(results)) > 1, "Increasing depth should change evaluation at least sometimes"
