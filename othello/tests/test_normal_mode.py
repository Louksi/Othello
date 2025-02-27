import pytest
import sys
import othello.parser as parser
from unittest.mock import patch
from unittest.mock import MagicMock
from othello.game_modes import BlitzGame, NormalGame
from othello.othello_board import BoardSize, Color, Bitboard


@pytest.fixture
def mock_blitz_game():
    """Fixture to create a BlitzGame with a mocked timer."""
    game = BlitzGame(BoardSize.EIGHT_BY_EIGHT)
    game.blitz_timer = MagicMock()
    game.blitz_timer.is_time_up.return_value = False
    return game


@pytest.fixture
def mock_game():
    """Fixture to create a mock OthelloGame object."""
    game = BlitzGame(BoardSize.EIGHT_BY_EIGHT)
    game.switch_player = MagicMock()
    game.board.black = MagicMock()
    game.board.white = MagicMock()
    game.board.size = BoardSize.EIGHT_BY_EIGHT
    return game


@pytest.fixture
def normal_game():
    """Fixture to create a NormalGame instance."""
    return NormalGame(BoardSize.EIGHT_BY_EIGHT)


@pytest.fixture
def mock_possible_moves():
    """Fixture to create a mock bitboard for possible moves."""
    bitboard = MagicMock()
    bitboard.get.side_effect = lambda x, y: (
        x, y) == (3, 2)
    return bitboard


def test_normal_mode_init(monkeypatch, normal_game):
    """
    Tests the initialization of a NormalGame object.
    Ensures the board size and initial player are correctly set.
    """
    monkeypatch.setattr(sys, 'argv', ["othello"])
    mode, _ = parser.parse_args()
    assert mode == parser.GameMode.NORMAL.value

    game = normal_game
    assert game.board.size == BoardSize.EIGHT_BY_EIGHT
    assert game.current_player == Color.BLACK

    monkeypatch.setattr(sys, 'argv', ["othello", "-s", "6"])
    _, parseConfig = parser.parse_args()
    assert parseConfig["size"] == 6
    game = NormalGame(parseConfig["size"])
    assert game.board.size == BoardSize(parseConfig["size"])


def test_normal_mode_size_init(monkeypatch, normal_game):
    monkeypatch.setattr(sys, 'argv', ["othello", "-s", "6"])
    _, parseConfig = parser.parse_args()
    assert parseConfig["size"] == 6
    game = NormalGame(parseConfig["size"])
    assert game.board.size == BoardSize(parseConfig["size"])


def test_display_board(capfd):
    game = NormalGame()
    game.display_board()

    captured = capfd.readouterr()
    assert str(game.board) in captured.out
    assert f"{game.current_player.name}'s turn ({game.current_player.value})" in captured.out


def test_normal_turn_switch(normal_game):
    """
    Tests that switch_player() correctly alternates the player.
    """
    game = normal_game
    assert game.current_player == Color.BLACK
    game.switch_player()
    assert game.current_player == Color.WHITE
    game.switch_player()
    assert game.current_player == Color.BLACK


def test_get_possible_moves(normal_game):
    """
    Tests that get_possible_moves() correctly returns the possible moves for the current player.
    The result is compared to the line_cap_move() result of the game board.
    """
    board = normal_game
    possible_moves = board.get_possible_moves()

    expected_moves = board.board.line_cap_move(board.current_player)
    assert possible_moves == expected_moves, f"Expected {expected_moves}, got {possible_moves}"


def test_game_over_both_players_no_moves(mock_game):
    """Test game over when both players have no valid moves."""
    game = mock_game
    game.current_player = Color.BLACK
    empty_moves = Bitboard(0)
    game.check_game_over(empty_moves)
    assert game.current_player == Color.WHITE
    result = game.check_game_over(empty_moves)
    assert result is True


def test_game_over_black_no_moves(mock_game):
    """Test game over when Black has no moves, White wins."""
    game = mock_game
    game.current_player = Color.BLACK
    empty_moves = Bitboard(0)

    assert game.check_game_over(empty_moves) == False


def test_game_over_white_no_moves(mock_game):
    """Test game over when White has no moves, Black wins."""
    game = mock_game
    game.current_player = Color.WHITE
    empty_moves = Bitboard(0)
    assert game.check_game_over(empty_moves) == False


def test_skip_turn(mock_game):
    """Test when a player has no moves but the game continues (turn is skipped)."""
    game = mock_game
    game.current_player = Color.BLACK
    game.switch_player = MagicMock()
    empty_moves = Bitboard(0)

    with patch("sys.exit") as mock_exit:
        assert game.check_game_over(empty_moves) is False
        mock_exit.assert_not_called()


def test_game_over_both_players_no_moves(mock_game):
    """Test when both players have no valid moves, the game is over."""
    game = mock_game
    game.current_player = Color.BLACK
    empty_moves = Bitboard(0)
    game.switch_player = MagicMock(
        side_effect=lambda: setattr(game, 'current_player', Color.WHITE))

    assert game.check_game_over(empty_moves) == False
    game.switch_player()
    assert game.current_player == Color.WHITE
    assert game.check_game_over(empty_moves) == True


def test_game_not_over(mock_game):
    """Test when there are valid moves, the game should not be over."""
    game = mock_game
    game.current_player = Color.BLACK
    valid_moves = Bitboard(1)

    assert game.check_game_over(valid_moves) is False


def test_display_possible_moves(mock_game, capsys):
    """Test if display_possible_moves correctly prints the possible moves."""
    game = mock_game
    possible_moves = MagicMock()
    possible_moves.get = MagicMock(side_effect=lambda x, y: (
        x, y) in [(2, 3), (4, 5)])

    game.display_possible_moves(possible_moves)
    captured = capsys.readouterr()

    expected_output = "Possible moves: \nc4 e6 \n"
    assert captured.out == expected_output


def test_process_move():
    '''Use Mock functions to play the game and process some illegal moves'''
    game = NormalGame(BoardSize.EIGHT_BY_EIGHT)
    possible_moves = MagicMock()
    possible_moves.get.side_effect = lambda x, y: (
        x, y) in [(3, 2), (4, 5)]

    game.board.play = MagicMock()

    assert game.process_move(3, 2, possible_moves) is True
    game.board.play.assert_called_with(3, 2)

    assert game.process_move(4, 5, possible_moves) is True
    game.board.play.assert_called_with(4, 5)

    with patch("builtins.print") as mock_print:
        assert game.process_move(1, 1, possible_moves) is False
        mock_print.assert_called_with(
            "Invalid move. Not a legal play. Try again.")


@pytest.mark.parametrize("user_input, expected_output", [
    ("a1", (0, 0)),  # 'a' -> 0, '1' -> 0
    ("h8", (7, 7)),  # 'h' -> 7, '8' -> 7
    ("c3", (2, 2)),  # 'c' -> 2, '3' -> 2
])
def test_get_player_move(monkeypatch, user_input, expected_output, normal_game):
    """
    Tests if get_player_move() correctly converts user input into (x, y) coordinates.

    The test uses the monkeypatch fixture to replace the built-in input() function
    with a mock function that returns the user_input param. The expected_output
    param is the expected result of the get_player_move() call.

    The test is parametrized to run for different inputs, to ensure that the
    function works correctly for different user inputs.
    """
    board = normal_game
    monkeypatch.setattr("builtins.input", lambda _: user_input)

    assert board.get_player_move() == expected_output


def test_switch_player():
    '''Tests valid switches between players'''
    game = NormalGame(BoardSize.EIGHT_BY_EIGHT)

    game.current_player = Color.BLACK
    game.switch_player()
    assert game.current_player == Color.WHITE

    game.switch_player()
    assert game.current_player == Color.BLACK
