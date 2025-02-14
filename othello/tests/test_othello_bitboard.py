from othello.bitboard import Bitboard
from othello.othello_bitboard import BoardSize, Color, OthelloBitboard
import pytest

""" black's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | | |C| | | | |
| | |C|O|X| | | |
| | | |X|O|C| | |
| | | | |C| | | |
| | | | | | | | |
| | | | | | | | |
"""


def test_line_cap_move_starting_pos():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    legal_mask = 0b0000000000000000000100000010000000000100000010000000000000000000
    cap = b.line_cap_move(Color.BLACK)
    assert cap.bits == legal_mask


""" black's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | | |C|C|C| | |
| | |C|O|O|X| | |
| | | |X|O|C| | |
| | | |C|O| | | |
| | | | |X|C| | |
| | | | | | | | |
"""


def test_line_cap_move_later_pos():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000000000000000000100000001000000011000000000000000000000000000
    b.black.bits = 0b0000000000010000000000000000100000100000000000000000000000000000
    legal_mask = 0b0000000000100000000010000010000000000100001110000000000000000000
    cap = b.line_cap_move(Color.BLACK)
    assert cap.bits == legal_mask


""" white's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | |C| |C| | | |
| | |X|X|X| | | |
| | |C|X|O| | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
"""


def test_line_cap_move_starting_pos_whites():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000000000000000000000000001000000000000000000000000000000000000
    b.black.bits = 0b0000000000000000000000000000100000011100000000000000000000000000
    legal_mask = 0b0000000000000000000000000000010000000000000101000000000000000000
    cap = b.line_cap_move(Color.WHITE)
    assert cap.bits == legal_mask


""" black's turn, C => candidate
| | | | | | | | |
| | | | | | | | |
| | | | | | |C| |
| | |C|O|O|X|C| |
| | |C|X|O| | | |
| | |C|C|O| | | |
| | | | |X| | | |
| | | | |C| | | |
"""


def test_line_cap_move_later_pos_whites():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000000000000000000100000001000000011000000000000000000000000000
    b.black.bits = 0b0000000000010000000000000000100000100000000000000000000000000000
    legal_mask = 0b0001000000000000000011000000010001000100010000000000000000000000
    cap = b.line_cap_move(Color.WHITE)
    assert cap.bits == legal_mask


""" black's turn, M => bit of the mask
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | |O|X| | | |
| | | |X|M| | | |
| | | | |M| | | |
| | | | | | | | |
| | | | | | | | |
"""


def test_line_cap_start_position():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    thruth_mask = 0b0000000000000000000100000001000000000000000000000000000000000000
    mask = b.line_cap(4, 5, Color.BLACK)
    assert thruth_mask == mask.bits


"""
  a b c d e f g h
1 _ _ _ _ O O O O
2 _ _ _ _ X X X O
3 _ _ O X _ _ X O
4 _ _ X O _ _ X O
5 _ _ O X C _ X O
6 _ _ _ X X X X O
7 _ _ O _ _ _ _ _
8 _ _ _ O _ _ _ _"""


def test_complex_position():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    b.white.bits = 0b0000100000000100100000001000010010001000100001001000000011110000
    b.black.bits = 0b0000000000000000011110000100100001000100010010000111000000000000
    cap = b.line_cap(4, 4, Color.WHITE)
    thruth_mask = 0b0000000000000000000010000001100000000000000000000000000000000000
    assert cap.bits == thruth_mask


def test__str__():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    starting_board = """  a b c d e f g h
1 _ _ _ _ _ _ _ _
2 _ _ _ _ _ _ _ _
3 _ _ _ _ _ _ _ _
4 _ _ _ O X _ _ _
5 _ _ _ X O _ _ _
6 _ _ _ _ _ _ _ _
7 _ _ _ _ _ _ _ _
8 _ _ _ _ _ _ _ _"""
    assert str(b) == starting_board
