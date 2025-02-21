import pytest
import sys
import othello.parser as parser
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
    game.board.play = MagicMock()
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
        x, y) == (3, 2)  # Only (3,2) is valid
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


def test_possible_moves_initial_state(normal_game):
    """
    Tests that possible_moves() returns the correct set of moves
    at the start of a normal game.
    """
    game = normal_game
    moves = game.get_possible_moves()
    assert isinstance(moves, Bitboard)
    assert moves.bits > 0


def test_check_game_not_over(mock_game):
    """Tests when there are valid moves available."""
    possible_moves = MagicMock()
    possible_moves.bits = 1

    assert mock_game.check_game_over(possible_moves) is False
    mock_game.switch_player.assert_not_called()


def test_display_possible_moves_with_moves(mock_game, capsys):
    """Tests that display_possible_moves prints the correct coordinates."""
    possible_moves = MagicMock()

    possible_moves.get = lambda x, y: (x, y) in [(2, 3), (5, 6)]  # c4 and f7

    mock_game.display_possible_moves(possible_moves)

    captured = capsys.readouterr()
    expected_output = "Possible moves: \nc4 f7 \n"
    assert captured.out == expected_output


def test_display_possible_moves_no_moves(mock_game, capsys):
    """Tests that display_possible_moves handles an empty move set."""
    possible_moves = MagicMock()

    possible_moves.get = lambda x, y: False

    mock_game.display_possible_moves(possible_moves)

    captured = capsys.readouterr()
    expected_output = "Possible moves: \n\n"
    assert captured.out == expected_output


def test_process_move_valid(mock_game, mock_possible_moves):
    """Tests that a valid move is processed correctly."""
    result = mock_game.process_move(3, 2, mock_possible_moves)
    assert result is True
    mock_game.board.play.assert_called_once_with(
        3, 2)  # Ensure play() is called


def test_process_move_invalid(mock_game, mock_possible_moves, capsys):
    """Tests that an invalid move is rejected."""
    result = mock_game.process_move(5, 5, mock_possible_moves)
    assert result is False
    captured = capsys.readouterr()
    assert "Invalid move. Not a legal play. Try again." in captured.out
    mock_game.board.play.assert_not_called()  # Ensure play() is NOT called
