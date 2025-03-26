import pytest
from unittest.mock import MagicMock, patch
from othello.othello_board import BoardSize, Color, Bitboard
from othello.command_parser import CommandKind, CommandParserException
from othello.othello.cli import NormalGame


@pytest.fixture
def normal_game():
    """Fixture to create a NormalGame instance with mocked board."""
    game = NormalGame(filename=None, board_size=BoardSize.EIGHT_BY_EIGHT)
    game.board = MagicMock()
    game.board.black = MagicMock()
    game.board.white = MagicMock()
    game.board.size = BoardSize.EIGHT_BY_EIGHT
    game.board.get_current_player.return_value = Color.BLACK
    return game


def test_check_game_over_when_board_says_game_over(normal_game):
    """Test that check_game_over returns True when board.is_game_over is True."""
    normal_game.board.is_game_over.return_value = True
    normal_game.board.black.popcount.return_value = 30
    normal_game.board.white.popcount.return_value = 34

    result = normal_game.check_game_over(MagicMock())

    assert result is True
    normal_game.board.is_game_over.assert_called_once()


def test_check_game_over_prints_correct_winner(normal_game, capsys):
    """Test that correct winner is printed when game is over."""
    normal_game.board.is_game_over.return_value = True
    normal_game.board.black.popcount.return_value = 40
    normal_game.board.white.popcount.return_value = 24

    normal_game.check_game_over(MagicMock())
    captured = capsys.readouterr()

    assert "Black wins!" in captured.out
    assert "Final score - Black: 40, White: 24" in captured.out


def test_check_game_over_prints_tie(normal_game, capsys):
    """Test that tie is printed when scores are equal."""
    normal_game.board.is_game_over.return_value = True
    normal_game.board.black.popcount.return_value = 32
    normal_game.board.white.popcount.return_value = 32

    normal_game.check_game_over(MagicMock())
    captured = capsys.readouterr()

    assert "The game is a tie!" in captured.out
    assert "Final score - Black: 32, White: 32" in captured.out


def test_check_game_over_skips_turn_when_no_moves(normal_game, capsys):
    """Test that turn is skipped when current player has no moves but game isn't over."""
    normal_game.board.is_game_over.return_value = False
    possible_moves = MagicMock()
    possible_moves.bits = 0

    result = normal_game.check_game_over(possible_moves)
    captured = capsys.readouterr()

    assert result is False
    assert "No valid moves for" in captured.out
    assert "Skipping turn" in captured.out


def test_check_game_over_continues_when_moves_exist(normal_game):
    """Test that game continues when moves exist."""
    normal_game.board.is_game_over.return_value = False
    possible_moves = MagicMock()
    possible_moves.bits = 1

    result = normal_game.check_game_over(possible_moves)

    assert result is False


def test_process_valid_move(normal_game):
    """Test that valid moves are processed correctly."""
    possible_moves = MagicMock()
    possible_moves.get.return_value = True
    normal_game.board.play = MagicMock()

    result = normal_game.process_move(3, 2, possible_moves)

    assert result is True
    normal_game.board.play.assert_called_once_with(3, 2)


def test_process_invalid_move(normal_game, capsys):
    """Test that invalid moves are rejected."""
    possible_moves = MagicMock()
    possible_moves.get.return_value = False

    result = normal_game.process_move(1, 1, possible_moves)
    captured = capsys.readouterr()

    assert result is False
    assert "Invalid move" in captured.out


def test_display_possible_moves(normal_game, capsys):
    """Test that possible moves are displayed correctly."""
    possible_moves = MagicMock()
    possible_moves.get.side_effect = lambda x, y: (x, y) in [(2, 3), (4, 5)]

    normal_game.display_possible_moves(possible_moves)
    captured = capsys.readouterr()

    assert "Possible moves:" in captured.out
    assert "c4" in captured.out
    assert "e6" in captured.out


@patch('builtins.input')
def test_play_loop_with_quit_command(mock_input, normal_game):
    """Test that quit command exits the game."""
    mock_input.return_value = 'q'
    normal_game.check_game_over = MagicMock(return_value=False)

    with patch('othello.game_modes.CommandParser') as mock_parser_class:
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_str.return_value = (CommandKind.QUIT,)

        with pytest.raises(SystemExit):
            normal_game.play()


@patch('builtins.input')
def test_play_loop_with_valid_move(mock_input, normal_game):
    """Test that valid move is processed correctly."""
    mock_input.side_effect = ['e3', 'q']
    normal_game.check_game_over = MagicMock(return_value=False)

    # Create a mock for possible moves
    mock_possible_moves = MagicMock()
    normal_game.get_possible_moves = MagicMock(
        return_value=mock_possible_moves)

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

        normal_game.process_move = MagicMock(return_value=True)

        with pytest.raises(SystemExit):
            normal_game.play()

        # Verify process_move was called with the correct arguments
        normal_game.process_move.assert_called_once_with(
            4, 2, mock_possible_moves)
