from othello.board_parser import BoardParser, BoardParserException
from othello.othello_board import BoardSize, OthelloBoard, Color
import pytest


def test_starting_board():
    board_raw = """
    
#comment
X
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X O _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _"""
    parser = BoardParser(board_raw)
    board = parser.parse()
    assert board == OthelloBoard(BoardSize.EIGHT_BY_EIGHT)


def test_more_complex_board():
    board_raw = """
#comment
 # another
O# ---
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O _
_ O _ X X _
_ _ _ _ _ _
"""
    truth_board = OthelloBoard(
        BoardSize.SIX_BY_SIX, current_player=Color.WHITE)
    truth_board.black.bits = 0b000000011000001100001000000000000000
    truth_board.white.bits = 0b000000000010010000000100000000000000
    parser = BoardParser(board_raw)
    board = parser.parse()
    assert board == truth_board


def test_illegal_boards():
    board_raw = """
#comment
 # another
O# ---
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O 
_ O _ X X _
_ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()
    board_raw = """
#comment
 # another
O# ---
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O _
_ O _ X X _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_illegal_color():
    board_raw = """
    
#comment
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X O _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()

    board_raw = """
    
#comment
K
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X O _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_two_colors():
    board_raw = """
#comment
 # another
O# ---
O
_ _ _ _ _ _ # other comment
_ _ _ _ _ _
_ _ O X _ _
_ _ X X O _
_ O _ X X _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_no_board():
    board_raw = """
#comment
 # another
O# ---
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_incoherent_turn_numbers():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d6
3. X c6 O b6
3. X d7
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_missing_black_play():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d6
2. X  O b6
3. X d7
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_illegal_history_move():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f6 O d6
2. X  O b6
3. X d7
"""

    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d7
2. X  O b6
3. X d7
"""

    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_incoherent_board():
    board_raw = """
O
_ R _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()
    board_raw = """
O
_ _ _ _ _ _
_ R _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
_ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_empty_board():
    board_raw = """"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


def test_next_char_on_eol():
    board_raw = """
O
"""
    b = BoardParser(board_raw)
    assert b._BoardParser__y == 0
    b._BoardParser__next_char()
    assert b._BoardParser__y == 1


def test_nextline_on_eof():
    board_raw = """"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b._BoardParser__next_line()


def test_board_illegal_size():
    board_raw = """
X
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ O X _ _ _ _ _ _
_ _ _ _ _ _ X O _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ _ _ _ _ _ _
"""
    b = BoardParser(board_raw)
    with pytest.raises(BoardParserException):
        b.parse()


"""
"""


def test_simple_history():
    board_raw = """
O
_ _ _ _ _ _ _ _
_ _ _ _ _ _ _ _ # other comment
_ _ _ _ _ _ _ _
_ _ _ O X _ _ _
_ _ _ X X X _ _
_ O O X _ _ _ _
_ _ _ X _ _ _ _
_ _ _ _ _ _ _ _

# commentaire
1. X f5 O d6
2. X c6 O b6
3. X d7
"""
    b = BoardParser(board_raw)
    o = b.parse()
    assert len(o.get_history()) == 5
