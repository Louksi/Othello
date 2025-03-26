import pytest
from unittest.mock import MagicMock, patch
from othello.cli import OthelloCLI
from othello.othello_board import Color


class TestBlitzMode:
    """Tests for blitz mode specific functionality"""

    @pytest.fixture
    def blitz_game(self):
        game = OthelloCLI(blitz_mode=True)
        game.board = MagicMock()
        game.board.get_current_player.return_value = Color.BLACK
        game.blitz_timer = MagicMock()
        return game

    def test_blitz_timer_switch(self, blitz_game):
        """Should switch timer on valid move"""
        # Setup mock moves
        mock_moves = MagicMock()
        mock_moves.get.return_value = True

        # Process a move
        blitz_game.process_move(3, 4, mock_moves)

        # Verify timer was switched to white (since current player is black)
        blitz_game.blitz_timer.change_player.assert_called_once_with('white')

    def test_blitz_timer_switch_white_to_black(self, blitz_game):
        """Should switch from white to black on valid move"""
        # Set current player to white
        blitz_game.board.get_current_player.return_value = Color.WHITE

        # Setup mock moves
        mock_moves = MagicMock()
        mock_moves.get.return_value = True

        # Process a move
        blitz_game.process_move(3, 4, mock_moves)

        # Verify timer was switched to black
        blitz_game.blitz_timer.change_player.assert_called_once_with('black')
