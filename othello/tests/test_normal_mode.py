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


def test_game_over_both_players_no_moves(mock_game):
    """Test game over when both players have no valid moves."""
    game = mock_game
    game.current_player = Color.BLACK  # Current player is Black
    empty_moves = Bitboard(0)
    game.check_game_over(empty_moves)  # called once to pass the turn
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
    game.switch_player = MagicMock()  # Mock switch_player
    empty_moves = Bitboard(0)

    with patch("sys.exit") as mock_exit:
        assert game.check_game_over(empty_moves) is False
        mock_exit.assert_not_called()  # sys.exit should NOT be called
        game.switch_player.assert_called_once()  # Ensure turn is skipped


def test_game_over_both_players_no_moves(mock_game):
    """Test when both players have no valid moves, the game is over."""
    game = mock_game
    game.current_player = Color.BLACK
    empty_moves = Bitboard(0)

    assert game.check_game_over(empty_moves) == True


def test_game_not_over(mock_game):
    """Test when there are valid moves, the game should not be over."""
    game = mock_game
    game.current_player = Color.BLACK
    valid_moves = Bitboard(1)  # Some valid moves

    assert game.check_game_over(valid_moves) is False  # Game continues
    game.switch_player.assert_called_once()
