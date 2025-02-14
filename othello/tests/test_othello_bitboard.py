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


""" black's turn, M => bit of the mask
| | | | | | | | |
| | | | | | | | |
| |X|O|O|C|O|O|X|
| | | |O|O|X| | |
| | |X|X|O| | | |
| | | | |O| | | |
| | | | |X| | | |
| | | | | | | | |

"""


def test_line_cap_complex_position():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    b.black.bits = 0b0000000000010000000000000000110000100000100000100000000000000000
    b.white.bits = 0b0000000000000000000100000001000000011000011011000000000000000000
    thruth_mask = 0b0000000000000000000100000001000000011000011111000000000000000000
    mask = b.line_cap(4, 2, Color.BLACK)
    assert thruth_mask == mask.bits


def test__str__():
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    starting_board = """ a b c d e f g h
0                
1                
2                
3      O X       
4      X O       
5                
6                
7                """
    assert str(b) == starting_board
