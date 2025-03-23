from othello.command_parser import CommandKind, PlayCommand
from unittest.mock import MagicMock, patch, call
import pytest
import sys
import time

import othello.parser as parser
from othello.command_parser import CommandKind, CommandParser
from unittest.mock import MagicMock, patch
from othello.blitz_timer import BlitzTimer
from othello.game_modes import BlitzGame, NormalGame
from othello.othello_board import BoardSize, Color, Bitboard


@pytest.fixture
def mock_blitz_game():
    """Fixture to create a BlitzGame with a mocked timer."""
    game = BlitzGame(filename=None, board_size=BoardSize.EIGHT_BY_EIGHT)
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

    game = BlitzGame(filename=None, board_size=BoardSize.EIGHT_BY_EIGHT)

    assert game.board.size == BoardSize.EIGHT_BY_EIGHT
    assert game.current_player == Color.BLACK
    assert isinstance(game.blitz_timer, BlitzTimer)


def test_blitz_game_init_with_custom_time():
    """Test BlitzGame initialization with a custom time parameter."""
    custom_time = 15
    game = BlitzGame(
        filename=None, board_size=BoardSize.EIGHT_BY_EIGHT, time=custom_time)

    assert game.blitz_timer.total_time == custom_time * 60


def test_blitz_game_init_with_int_board_size():
    """Test BlitzGame initialization with an integer board size."""
    game = BlitzGame(filename=None, board_size=8)
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


def test_blitz_check_game_over_board_full(mock_blitz_game):
    """Test game over condition when board is full based on popcount."""
    game = mock_blitz_game

    # First ensure time isn't up for either player
    game.blitz_timer.is_time_up.return_value = False

    # Mock parent class's check_game_over to isolate our test
    original_super = super(BlitzGame, game).check_game_over

    # Use a patching approach to call the real method but control the outcome
    with patch('builtins.super') as mock_super:
        mock_parent_game = MagicMock()
        mock_super.return_value = mock_parent_game

        # 1. Test when board is full and black wins
        mock_parent_game.check_game_over.return_value = True

        valid_moves = Bitboard(1)  # Some valid moves exist
        assert game.check_game_over(valid_moves) is True

        # Verify super().check_game_over was called
        mock_parent_game.check_game_over.assert_called_with(valid_moves)


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_command_quit(mock_print, mock_input, mock_blitz_game):
    """Test the quit command in the play loop."""
    mock_input.return_value = 'quit'
    game = mock_blitz_game

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_str.return_value = (CommandKind.QUIT, None)

        # Mock internal methods to isolate the play loop
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    # Verify the expected flow
    assert game.display_board.call_count == 1
    assert game.get_possible_moves.call_count == 1


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_command_forfeit(mock_print, mock_input, mock_blitz_game):
    """Test the forfeit command in the play loop."""
    mock_input.return_value = 'forfeit'
    game = mock_blitz_game
    game.current_player = Color.BLACK

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_str.return_value = (CommandKind.FORFEIT, None)

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()
        game.switch_player = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    game.switch_player.assert_called_once()
    mock_print.assert_any_call("BLACK forfeited.")


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_command_help(mock_print, mock_input, mock_blitz_game):
    """Test the help command in the play loop."""
    mock_input.return_value = 'help'
    game = mock_blitz_game

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Set up the parser to return HELP first, then QUIT when called again
        mock_parser.parse_str.side_effect = [
            (CommandKind.HELP, None),
            (CommandKind.QUIT, None)
        ]

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    mock_parser.print_help.assert_called_once()


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_command_restart(mock_print, mock_input, mock_blitz_game):
    """Test the restart command in the play loop."""
    mock_input.return_value = 'restart'
    game = mock_blitz_game

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Set up the parser to return RESTART first, then QUIT when called again
        mock_parser.parse_str.side_effect = [
            (CommandKind.RESTART, None),
            (CommandKind.QUIT, None)
        ]

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()
        game.board = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    game.board.restart.assert_called_once()


@patch('builtins.input')
def test_blitz_play_command_save_and_quit(mock_input, mock_blitz_game):
    """Test the save and quit command in the play loop."""
    mock_input.return_value = 'save'
    game = mock_blitz_game

    with patch('othello.game_modes.CommandParser') as mock_parser_class, \
            patch('othello.game_modes.save_board_state_history') as mock_save:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_str.return_value = (CommandKind.SAVE_AND_QUIT, None)

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    mock_save.assert_called_once_with(game.board)


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_valid_move(mock_print, mock_input, mock_blitz_game):
    """Test playing a valid move in the play loop."""
    mock_input.return_value = 'a1'
    game = mock_blitz_game
    game.current_player = Color.BLACK

    play_command = MagicMock()
    play_command.x_coord = 0  # 'a'
    play_command.y_coord = 0  # '1'

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Set up the parser to return PLAY_MOVE first, then QUIT when called again
        mock_parser.parse_str.side_effect = [
            (CommandKind.PLAY_MOVE, play_command),
            (CommandKind.QUIT, None)
        ]

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()
        game.process_move = MagicMock(return_value=True)
        game.switch_player = MagicMock()
        game.display_time = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    game.process_move.assert_called_once_with(0, 0, Bitboard(1))
    game.switch_player.assert_called_once()
    game.display_time.assert_called_once()


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_invalid_move(mock_print, mock_input, mock_blitz_game):
    """Test playing an invalid move in the play loop."""
    mock_input.return_value = 'a1'
    game = mock_blitz_game

    play_command = MagicMock()
    play_command.x_coord = 0  # 'a'
    play_command.y_coord = 0  # '1'

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Set up the parser to return PLAY_MOVE first, then QUIT when called again
        mock_parser.parse_str.side_effect = [
            (CommandKind.PLAY_MOVE, play_command),
            (CommandKind.QUIT, None)
        ]

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()
        game.process_move = MagicMock(return_value=False)  # Invalid move
        game.switch_player = MagicMock()

        with pytest.raises(SystemExit) as e:
            game.play()

        assert e.value.code == 0

    game.process_move.assert_called_once_with(0, 0, Bitboard(1))
    # Should not switch player on invalid move
    game.switch_player.assert_not_called()


@patch('builtins.input')
@patch('builtins.print')
def test_blitz_play_parser_exception(mock_print, mock_input, mock_blitz_game):
    """Test handling of parser exceptions in the play loop."""
    from othello.command_parser import CommandParserException

    mock_input.return_value = 'invalid'
    game = mock_blitz_game

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser

        # Set up the parser to raise an exception first, then return QUIT when called again
        mock_parser.parse_str.side_effect = [
            CommandParserException("Invalid command"),
            (CommandKind.QUIT, None)
        ]

        # Mock internal methods
        game.display_board = MagicMock()
        game.get_possible_moves = MagicMock(return_value=Bitboard(1))
        game.check_game_over = MagicMock(return_value=False)
        game.display_possible_moves = MagicMock()

        with patch('othello.game_modes.log.log_error_message') as mock_log:
            with pytest.raises(SystemExit) as e:
                game.play()

            assert e.value.code == 0

    mock_log.assert_called_once()
    mock_print.assert_any_call("Invalid command. Please try again.")
