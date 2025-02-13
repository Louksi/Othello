import pytest
import sys
import othello.parser as parser
from othello.blitz_mode import BlitzMode
from othello.othello_bitboard import BoardSize


def test_blitzMode(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "30"])
    mode, parseConfig = parser.parse_args()
    assert mode == parser.GameMode.BLITZ
    assert parseConfig["bTime"] == 30
    # parser okay now init the game
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    assert game.time_limit == 30
