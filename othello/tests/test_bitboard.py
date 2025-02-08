import pytest
from copy import copy
from othello.bitboard import Bitboard, Direction


def test_init_2():
    b_2 = Bitboard(2)

    assert b_2.mask == 0b1111
    assert b_2.west_mask == 0b1010
    assert b_2.east_mask == 0b0101


def test_init_8():
    b_8 = Bitboard(8)

    assert b_8.mask == 0b1111111111111111111111111111111111111111111111111111111111111111
    assert b_8.west_mask == 0b1111111011111110111111101111111011111110111111101111111011111110
    assert b_8.east_mask == 0b0111111101111111011111110111111101111111011111110111111101111111


def test_oob_access():
    b = Bitboard(6)

    with pytest.raises(IndexError):
        b.set(0, 6, True)


def test_set():
    b = Bitboard(4)
    b.set(0, 0, True)
    b.set(3, 3, True)
    b.set(1, 1, True)

    assert b.bits == 0b1000000000100001
    b.set(3, 3, False)

    assert b.bits == 0b0000000000100001


def test_get():
    b = Bitboard(6)
    b.set(0, 3, True)
    b.set(4, 5, True)

    assert b.get(0, 3) and b.get(4, 5) and not b.get(4, 2) and not b.get(0, 0)


"""
| | | |·| |
|·| | | | |
| | | | |·|
| | |·| | |
|·| | | | |
"""
pytest.b = Bitboard(5)
pytest.b.bits = 0b0000100100100000000101000


def test_shift_n():
    """
    |·| | | | |
    | | | | |·|
    | | |·| | |
    |·| | | | |
    | | | | | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.NORTH)

    assert shifted_b.bits == 0b0000000001001001000000001


def test_shift_s():
    """
    | | | | | |
    | | | |·| |
    |·| | | | |
    | | | | |·|
    | | |·| | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.SOUTH)

    assert (shifted_b.bits & shifted_b.mask) == (
        0b0010010000000010100000000 & shifted_b.mask)


def test_shift_w():
    """
    | | |·| | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    | | | | | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.WEST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0000000010010000000000100 & shifted_b.mask)


def test_e():
    """
    | | | | |·|
    | |·| | | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.EAST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0001001000000000001010000 & shifted_b.mask)


def test_ne():
    """
    | |·| | | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    | | | | | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.NORTH_EAST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0000000010010000000000010 & shifted_b.mask
    )


def test_nw():
    """
    | | | | | |
    | | | |·| |
    | |·| | | |
    | | | | | |
    | | | | | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.NORTH_WEST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0000000000000100100000000 & shifted_b.mask
    )


def test_se():
    """
    | | | | | |
    | | | | |·|
    | |·| | | |
    | | | | | |
    | | | |·| |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.SOUTH_EAST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0100000000000101000000000 & shifted_b.mask
    )


def test_sw():
    """
    | | | | | |
    | | |·| | |
    | | | | | |
    | | | |·| |
    | |·| | | |
    """
    b = copy(pytest.b)
    shifted_b = b.shift(Direction.SOUTH_WEST)
    assert (shifted_b.bits & shifted_b.mask) == (
        0b0001001000000000010000000 & shifted_b.mask
    )


def test_str():
    assert str(pytest.b) ==\
        """| | | |·| |
|·| | | | |
| | | | |·|
| | |·| | |
|·| | | | |"""
# ·
