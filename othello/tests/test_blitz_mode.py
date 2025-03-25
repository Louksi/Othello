from othello.command_parser import CommandKind, PlayCommand
from unittest.mock import MagicMock, patch, call
import pytest
from unittest.mock import MagicMock, patch
from othello.game_modes import BlitzGame
from othello.othello_board import BoardSize, Color
from othello.command_parser import CommandKind
from othello.controllers import GameController


@pytest.fixture
def blitz_game():
    """Fixture to create a BlitzGame instance with mocked controller."""
    game = BlitzGame(filename=None, board_size=BoardSize.EIGHT_BY_EIGHT)

    # Create a proper mock controller with all needed attributes
    controller_mock = MagicMock()
    controller_mock.get_current_player.return_value = Color.BLACK
    controller_mock.is_game_over.return_value = False
    controller_mock.size = BoardSize.EIGHT_BY_EIGHT  # Add size attribute

    # Mock the board methods needed for score calculation
    controller_mock.get_pieces_count.side_effect = lambda color: 30 if color == Color.BLACK else 34

    game.board = controller_mock

    # Mock timer
    game.blitz_timer = MagicMock()
    game.blitz_timer.is_time_up.return_value = False

    return game


def test_blitz_game_init_with_default_time():
    """Test BlitzGame initialization with default time."""
    game = BlitzGame(filename=None, board_size=BoardSize.EIGHT_BY_EIGHT)
    assert hasattr(game, 'blitz_timer')


def test_blitz_game_init_with_custom_time():
    """Test BlitzGame initialization with custom time."""
    custom_time = 10
    game = BlitzGame(
        filename=None, board_size=BoardSize.EIGHT_BY_EIGHT, time=custom_time)
    assert game.blitz_timer.total_time == custom_time * 60


@patch('sys.exit')
def test_switch_player_black_time_up(mock_exit, blitz_game):
    """Test switch_player when black's time is up."""
    blitz_game.blitz_timer.is_time_up.return_value = True
    blitz_game.switch_player()
    mock_exit.assert_called_once_with(0)


@patch('sys.exit')
def test_switch_player_white_time_up(mock_exit, blitz_game):
    """Test switch_player when white's time is up."""
    blitz_game.board.get_current_player.return_value = Color.WHITE
    blitz_game.blitz_timer.is_time_up.return_value = True
    blitz_game.switch_player()
    mock_exit.assert_called_once_with(0)


def test_switch_player_normal_case(blitz_game):
    """Test normal player switching without time up."""
    blitz_game.switch_player()
    blitz_game.blitz_timer.change_player.assert_called_once_with('white')


def test_display_time(blitz_game, capsys):
    """Test display_time outputs timer information."""
    blitz_game.blitz_timer.display_time.return_value = "Black: 5:00 | White: 4:30"
    blitz_game.display_time()
    captured = capsys.readouterr()
    assert "Black: 5:00 | White: 4:30" in captured.out


@patch('sys.exit')
def test_check_game_over_black_time_up(mock_exit, blitz_game):
    """Test check_game_over when black's time is up."""
    blitz_game.blitz_timer.is_time_up.side_effect = lambda p: p == 'black'
    blitz_game.check_game_over(MagicMock())
    mock_exit.assert_called_once_with(0)


@patch('sys.exit')
def test_switch_player_white_time_up(mock_exit, blitz_game):
    """Test switch_player when white's time is up."""
    blitz_game.board.get_current_player.return_value = Color.WHITE
    blitz_game.blitz_timer.is_time_up.side_effect = lambda p: p == 'white'
    blitz_game.switch_player()
    mock_exit.assert_called_once_with(0)


def test_switch_player_normal_case(blitz_game):
    """Test normal player switching without time up."""
    blitz_game.switch_player()
    blitz_game.board.play.assert_called_once_with(-1, -1)  # Verify dummy move
    blitz_game.blitz_timer.change_player.assert_called_once_with('white')


@patch('builtins.input')
def test_play_loop_with_time_display(mock_input, blitz_game):
    """Test that time is displayed during gameplay."""
    mock_input.side_effect = ['e3', 'q']
    blitz_game.check_game_over = MagicMock(return_value=False)

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        play_command = MagicMock()
        play_command.x_coord = 4
        play_command.y_coord = 2
        mock_parser.parse_str.side_effect = [
            (CommandKind.PLAY_MOVE, play_command),
            (CommandKind.QUIT,)
        ]

        blitz_game.process_move = MagicMock(return_value=True)
        blitz_game.display_time = MagicMock()

        with pytest.raises(SystemExit):
            blitz_game.play()

        blitz_game.display_time.assert_called()
