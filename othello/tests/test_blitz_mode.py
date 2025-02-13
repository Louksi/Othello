import pytest
import sys
import time
import othello.parser as parser
from othello.blitz_mode import BlitzMode
from othello.othello_bitboard import BoardSize, Color


def test_blitzMode_init(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "30"])
    mode, parseConfig = parser.parse_args()
    assert mode == parser.GameMode.BLITZ
    assert parseConfig["bTime"] == 30

    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)

    assert game.board.size == BoardSize.EIGHT_BY_EIGHT
    assert game.current_player == Color.BLACK


def test_turn_switch():
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    assert game.current_player == Color.BLACK
    game.switch_turn()
    assert game.current_player == Color.WHITE
    game.switch_turn()
    assert game.current_player == Color.BLACK
