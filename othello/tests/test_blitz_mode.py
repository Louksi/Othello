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

    # Initialize the game and check time limit
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    assert game.time_limit == 30
    assert game.time_black == 30
    assert game.time_white == 30
    assert game.current_player == Color.BLACK


def test_time_decrease():
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    start_time = game.time_black
    time.sleep(1)
    game.switch_turn()
    assert game.time_black < start_time


def test_turn_switch():
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    assert game.current_player == Color.BLACK
    game.switch_turn()
    assert game.current_player == Color.WHITE
    game.switch_turn()
    assert game.current_player == Color.BLACK


def test_timeout():
    game = BlitzMode(BoardSize.EIGHT_BY_EIGHT)
    game.time_black = 1
    time.sleep(2)
    result = game.switch_turn()
    assert not result
