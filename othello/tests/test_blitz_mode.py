import pytest
import sys
import time
import othello.parser as parser
from othello.blitz_mode import BlitzMode
from othello.othello_board import BoardSize, Color


def test_blitzMode_init(monkeypatch):
    """
    Tests the initialization of a BlitzMode object.

    Verifies that it correctly takes the board size and current player from the
    parser configuration.
    """
    monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "30"])
    mode, parseConfig = parser.parse_args()
    assert mode == parser.GameMode.BLITZ
    assert parseConfig["bTime"] == 30

    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)

    assert game.board.size == BoardSize.EIGHT_BY_EIGHT
    assert game.current_player == Color.BLACK


def test_turn_switch():
    """
    Tests that the switch_turn() method correctly switches the current player.

    Verifies that switching the player once switches to the other color and
    switching it twice switches back to the original color.
    """
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    assert game.current_player == Color.BLACK
    game.switch_turn()
    assert game.current_player == Color.WHITE
    game.switch_turn()
    assert game.current_player == Color.BLACK
