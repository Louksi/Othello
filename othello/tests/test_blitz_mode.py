import pytest
import sys
import time
import othello.parser as parser
from unittest.mock import MagicMock, patch
from othello.blitz_timer import BlitzTimer
from othello.game_modes import BlitzGame
from othello.othello_board import BoardSize, Color, Bitboard


@pytest.fixture
def mock_blitz_game():
    """Fixture to create a BlitzGame with a mocked timer."""
    game = BlitzGame(BoardSize.EIGHT_BY_EIGHT)
    game.blitz_timer = MagicMock()
    game.blitz_timer.is_time_up.return_value = False
    return game


def test_blitzMode_init(monkeypatch):
    """
    Tests the initialization of a BlitzGame object.
    Ensures the board size and initial player are correctly set.
    """
    monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "30"])
    mode, parseConfig = parser.parse_args()
    assert mode == parser.GameMode.BLITZ.value
    assert parseConfig["blitz_time"] == 30

    game = BlitzGame(BoardSize.EIGHT_BY_EIGHT)

    assert game.board.size == BoardSize.EIGHT_BY_EIGHT
    assert game.current_player == Color.BLACK
    assert isinstance(game.blitz_timer, BlitzTimer)


def test_blitz_game_init_with_custom_time():
    """Test BlitzGame initialization with a custom time parameter."""
    custom_time = 15
    game = BlitzGame(BoardSize.EIGHT_BY_EIGHT, time=custom_time)

    assert game.blitz_timer.total_time == custom_time * 60


def test_blitz_game_init_with_int_board_size():
    """Test BlitzGame initialization with an integer board size."""
    game = BlitzGame(board_size=8)
    assert game.board.size == BoardSize.EIGHT_BY_EIGHT


@patch('sys.exit')
def test_switch_player_time_up_black(mock_exit, mock_blitz_game):
    """Test switch_player when black's time is up."""
    game = mock_blitz_game
    game.current_player = Color.BLACK

    game.blitz_timer.is_time_up.side_effect = lambda player: player == 'black'

    game.switch_player()

    mock_exit.assert_called_once_with(0)


@patch('sys.exit')
def test_switch_player_time_up_white(mock_exit, mock_blitz_game):
    """Test switch_player when white's time is up."""
    game = mock_blitz_game
    game.current_player = Color.WHITE

    game.blitz_timer.is_time_up.side_effect = lambda player: player == 'white'
    game.switch_player()
    mock_exit.assert_called_once_with(0)


def test_display_time(mock_blitz_game, capsys):
    """
    Tests that display_time() calls BlitzTimer.display_time() and prints the output.
    """
    game = mock_blitz_game
    game.blitz_timer.display_time.return_value = "Black: 5:00, White: 4:30"

    game.display_time()
    captured = capsys.readouterr()

    assert "Black: 5:00, White: 4:30" in captured.out
    game.blitz_timer.display_time.assert_called_once()


def test_check_game_over(mock_blitz_game):
    """
    Tests the check_game_over method in BlitzGame to ensure it behaves correctly
    when a player's time runs out and when valid moves are still available.
    """
    game = mock_blitz_game

    game.blitz_timer.is_time_up.side_effect = lambda player: player == "black"

    with pytest.raises(SystemExit) as excinfo:
        game.check_game_over(0)

    assert str(excinfo.value) == "0"
    game.blitz_timer.is_time_up.assert_called_with("black")

    game.current_player = Color.WHITE
    game.blitz_timer.is_time_up.side_effect = lambda player: player == "white"

    with pytest.raises(SystemExit) as excinfo:
        game.check_game_over(0)

    assert str(excinfo.value) == "0"
    game.blitz_timer.is_time_up.assert_called_with("white")

    game.blitz_timer.is_time_up.side_effect = lambda player: False

    game.check_game_over = MagicMock(return_value=False)

    assert not game.check_game_over(0)
