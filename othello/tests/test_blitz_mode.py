import pytest
from unittest.mock import MagicMock, Mock, patch
from othello.cli import OthelloCLI
from othello.othello_board import Color


class TestBlitzMode:
    """Tests for blitz mode specific functionality"""

    @pytest.fixture
    def blitz_game(self):
        mock_board = MagicMock()
        game = OthelloCLI(mock_board, blitz_mode=True)
        game.controller = MagicMock()
        game.controller.get_current_player.return_value = Color.BLACK
        game.blitz_timer = MagicMock()
        return game

    @pytest.fixture
    def blitz_game_white_timer_over(self):
        # Create a mock controller
        mock_controller = MagicMock()
        mock_controller.get_current_player.return_value = Color.BLACK
        mock_controller.is_game_over.return_value = (
            False  # Game isn't over due to board state
        )

        # Create the game with blitz mode enabled
        game = OthelloCLI(mock_controller, blitz_mode=True)

        # Replace the real BlitzTimer with a mock
        game.blitz_timer = MagicMock()

        # Set up the blitz timer to indicate white's timer is over
        game.blitz_timer.is_time_up("white").return_value = True  # Time is over
        game.blitz_timer.get_current_player.return_value = (
            Color.WHITE
        )  # For white player

        return game

    def test_blitz_timer_switch(self, blitz_game):
        """Should switch timer on valid move"""
        # Setup mock moves
        mock_moves = MagicMock()
        mock_moves.get.return_value = True

        # Process a move
        blitz_game.process_move(3, 4, mock_moves)

        # Verify timer was switched to white (since current player is black)
        blitz_game.blitz_timer.change_player.assert_called_once_with("white")

    def test_blitz_timer_switch_white_to_black(self, blitz_game):
        """Should switch from white to black on valid move"""
        # Set current player to white
        blitz_game.controller.get_current_player.return_value = Color.WHITE

        # Setup mock moves
        mock_moves = MagicMock()
        mock_moves.get.return_value = True

        # Process a move
        blitz_game.process_move(3, 4, mock_moves)

        # Verify timer was switched to black
        blitz_game.blitz_timer.change_player.assert_called_once_with("black")

    def test_init_game_mode(self):
        mock_controller = Mock()
        game = OthelloCLI(mock_controller, blitz_mode=True)
        assert game.blitz_mode
        assert hasattr(game, "blitz_timer")

    def test_check_game_over_blitz(self, blitz_game_white_timer_over):

        assert blitz_game_white_timer_over.check_game_over(
            blitz_game_white_timer_over.controller.get_possible_moves(
                blitz_game_white_timer_over.controller.get_current_player()
            )
        )
