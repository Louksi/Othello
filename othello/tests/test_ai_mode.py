import pytest
import sys
from unittest.mock import MagicMock, patch, call
from othello.command_parser import CommandKind, CommandParser
from othello.game_modes import AIMode, NormalGame
from othello.othello_board import BoardSize, Color, Bitboard


class TestAIMode:
    @pytest.fixture
    def ai_mode(self):
        """Fixture to create a basic AIMode instance"""
        # Fix: Use a string instead of Color enum
        return AIMode(board_size=BoardSize.EIGHT_BY_EIGHT, ai_color="black", depth=3)
