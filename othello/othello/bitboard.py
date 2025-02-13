from __future__ import annotations  # used for self-referencing classes...

from enum import Enum, auto
from copy import copy


class Direction(Enum):
    NORTH = auto()
    SOUTH = auto()
    EAST = auto()
    WEST = auto()
    NORTH_EAST = auto()
    NORTH_WEST = auto()
    SOUTH_EAST = auto()
    SOUTH_WEST = auto()


class Bitboard:
    def __init__(self, size: int, bits=0):
        """
        Initializes a Bitboard with a given size and bits.

        The size of the bitboard is given by the `size` parameter. The `bits`
        parameter is optional and defaults to 0. It is used to set the initial
        state of the bitboard. The `mask`, `west_mask`, and `east_mask`
        attributes of the bitboard are also initialized during this method.

        :param size: The size of the bitboard.
        :type size: int
        :param bits: The initial state of the bitboard, defaults to 0.
        :type bits: int, optional
        """
        self.size = size
        self.mask = 0
        self.west_mask = 0
        self.east_mask = 0
        for i in range(size * size):
            self.mask |= (1 << i)
            self.west_mask |= (1 << i) if i % self.size != 0 else 0
            self.east_mask |= (1 << i) if i % self.size != self.size-1 else 0
        self.bits = bits

    def set(self, x: int, y: int, value: bool) -> None:
        """
        Sets the bit at `x`:`y` to the truth value of `value` (0 if False, else 1).

        :param x: The x coordinate in the board representation.
        :type x: int
        :param y: The y coordinate in the board representation.
        :type y: int
        :param value: The truth value of the bit at `x`:`y`.
        :type value: bool
        """
        bit_idx = self.__coords_to_bit_idx(x, y)
        self.__check_bit_idx_is_legal(bit_idx)
        if value:
            # we simply need to set the corresponding bit to 1 using binary-or
            self.bits |= (1 << bit_idx)
        else:
            # a little trickier, we need to generate a mask that has a 0 at the location
            # we want to set to 0, then use a binary with the mask effectively
            # keeping every set bit but the one we are trying to set to 0
            mask = self.mask
            mask ^= (1 << bit_idx)
            self.bits &= mask

    def get(self, x: int, y: int) -> bool:
        """
        Get the truth value of a bit `x`:`y` (True if 1, else False).

        :param x: The x coordinate in the board representation.
        :type x: int
        :param y: The y coordinate in the board representation.
        :returns: The value of thus bit
        :rtype: int
        """
        bit_idx = self.__coords_to_bit_idx(x, y)
        self.__check_bit_idx_is_legal(bit_idx)
        mask = 1 << bit_idx
        rez = self.bits & mask
        return rez != 0

    def shift(self, dir: Direction):
        """
        Shift a bit in direction `dir`.

        :param dir: The direction of the shift
        :type Direction:
        :returns: The result of said shift if it exists
        :rtype: int
        """
        if dir == Direction.NORTH:
            return self.__shift_n()
        elif dir == Direction.SOUTH:
            return self.__shift_s()
        elif dir == Direction.EAST:
            return self.__shift_e()
        elif dir == Direction.WEST:
            return self.__shift_w()
        elif dir == Direction.NORTH_EAST:
            return self.__shift_ne()
        elif dir == Direction.NORTH_WEST:
            return self.__shift_nw()
        elif dir == Direction.SOUTH_EAST:
            return self.__shift_se()
        elif dir == Direction.SOUTH_WEST:
            return self.__shift_sw()

    def __shift_w(self) -> Bitboard:
        """
        Shift all the bits to the west (left).

        :returns: The result of the shift if it exists
        :rtype: int
        """

        clone = copy(self)
        clone.bits = ((self.bits >> 1) & self.east_mask) & self.mask
        return clone

    def __shift_e(self) -> Bitboard:
        """
        Shift all the bits to the east (right).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = ((self.bits << 1) & self.west_mask) & self.mask
        return clone

    def __shift_n(self) -> Bitboard:
        """
        Shift all the bits to the north (up).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits >> self.size) & self.mask
        return clone

    def __shift_s(self) -> Bitboard:
        """
        Shift all the bits to the south (down).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits << self.size) & self.mask
        return clone

    def __shift_ne(self) -> Bitboard:
        """
        Shift all the bits to the north-east (up-right).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits >> self.size-1 & self.west_mask) & self.mask
        return clone

    def __shift_nw(self) -> Bitboard:
        """
        Shift all the bits to the north-west (up-left).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits >> self.size+1 & self.east_mask) & self.mask
        return clone

    def __shift_se(self) -> Bitboard:
        """
        Shift all the bits to the south-east (down-right).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits << self.size+1 & self.west_mask) & self.mask
        return clone

    def __shift_sw(self) -> Bitboard:
        """
        Shift all the bits to the south-west (down-left).

        :returns: The result of the shift if it exists
        :rtype: int
        """
        clone = copy(self)
        clone.bits = (self.bits << self.size-1 & self.east_mask) & self.mask
        return clone

    def __coords_to_bit_idx(self, x: int, y: int) -> int:
        """
        Convert board coordinates to a bit index.

        This method takes the coordinates of a square on the board, and
        returns the corresponding bit index in the bitboard.

        :param x: The x coordinate of the square.
        :type x: int
        :param y: The y coordinate of the square.
        :type y: int
        :returns: The bit index of the square.
        :rtype: int
        """
        return y * self.size + x

    def __check_bit_idx_is_legal(self, bit_idx: int) -> None:
        """
        Checks if the given bit index is within legal bounds.

        This method ensures that the bit index is within the valid range for the bitboard,
        which is from 0 to size*size - 1. If the index is out of bounds, an IndexError is raised.

        :param bit_idx: The bit index to check.
        :type bit_idx: int

        :raises IndexError: If the bit index is out of legal bounds.
        """

        if not 0 <= bit_idx < (self.size * self.size):
            # avoiding out-of-bound access
            raise IndexError

    def __and__(self, o: Bitboard) -> Bitboard:
        """
        Compute the logical AND of two bitboards.

        This method takes a bitboard `o` and computes the logical AND of the
        current bitboard with `o`. The result is a new bitboard that has a
        1 in each position where both the current bitboard and `o` have a 1.

        :param o: The bitboard to compute the logical AND with.
        :type o: Bitboard
        :return: A bitboard that is the logical AND of the current bitboard and `o`.
        :rtype: Bitboard
        """
        r = copy(self)
        return Bitboard(self.size, r.bits & o.bits)

    def __or__(self, o: Bitboard) -> Bitboard:
        """
        Compute the logical OR of two bitboards.

        This method takes a bitboard `o` and computes the logical OR of the
        current bitboard with `o`. The result is a new bitboard that has a
        1 in each position where either the current bitboard or `o` have a 1.

        :param o: The bitboard to compute the logical OR with.
        :type o: Bitboard
        :return: A bitboard that is the logical OR of the current bitboard and `o`.
        :rtype: Bitboard
        """
        r = copy(self)
        return Bitboard(self.size, r.bits | o.bits)

    def __xor__(self, o: Bitboard) -> Bitboard:
        """
        Compute the logical XOR of two bitboards.

        This method takes a bitboard `o` and computes the logical XOR of the
        current bitboard with `o`. The result is a new bitboard that has a
        1 in each position where either the current bitboard or `o` have a 1,
        but not both.

        :param o: The bitboard to compute the logical XOR with.
        :type o: Bitboard
        :return: A bitboard that is the logical XOR of the current bitboard and `o`.
        :rtype: Bitboard
        """
        r = copy(self)
        return Bitboard(self.size, r.bits ^ o.bits)

    def __str__(self) -> str:
        """
        Returns a string representation of the bitboard. Mostly for debugging.

        :return: A string representation of the bitboard showing its x and y dimension. "·" for non-empty cases, " " for empty ones.
        :rtype str
        """
        return "\n".join(
            "".join(
                f"{'|' if x == 0 else ''}{'·' if self.get(x, y) else ' '}|" for x in range(self.size)
            ) for y in range(self.size)
        )
