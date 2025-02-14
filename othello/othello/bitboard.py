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
        else:
            return self.__shift_sw()

    def popcount(self) -> int:
        """
        popcount (SWAR) simple python port supporting arbitrary-sized bitboards because python is very permissive...

        :returns: The number of hot bits in the bitboard representation
        :rtype: int
        """
        sum = 0
        n = self.bits
        while n > 0:
            chunk_n = (n & 0xFFFFFFFFFFFFFFFF)
            chunk_n = (chunk_n & 0x5555555555555555) + \
                ((chunk_n >> 1) & 0x5555555555555555)
            chunk_n = (chunk_n & 0x3333333333333333) + \
                ((chunk_n >> 2) & 0x3333333333333333)
            chunk_n = (chunk_n & 0x0F0F0F0F0F0F0F0F) + \
                ((chunk_n >> 4) & 0x0F0F0F0F0F0F0F0F)
            chunk_n = (chunk_n & 0x00FF00FF00FF00FF) + \
                ((chunk_n >> 8) & 0x00FF00FF00FF00FF)
            chunk_n = (chunk_n & 0x0000FFFF0000FFFF) + \
                ((chunk_n >> 16) & 0x0000FFFF0000FFFF)
            chunk_n = (chunk_n & 0x00000000FFFFFFFF) + \
                ((chunk_n >> 32) & 0x00000000FFFFFFFF)
            sum += chunk_n
            n >>= 64
        return sum

    def __shift_w(self) -> Bitboard:
        clone = copy(self)
        clone.bits = ((self.bits >> 1) & self.east_mask) & self.mask
        return clone

    def __shift_e(self) -> Bitboard:
        clone = copy(self)
        clone.bits = ((self.bits << 1) & self.west_mask) & self.mask
        return clone

    def __shift_n(self) -> Bitboard:
        clone = copy(self)
        clone.bits = (self.bits >> self.size) & self.mask
        return clone

    def __shift_s(self) -> Bitboard:
        clone = copy(self)
        clone.bits = (self.bits << self.size) & self.mask
        return clone

    def __shift_ne(self) -> Bitboard:
        clone = copy(self)
        clone.bits = (self.bits >> self.size-1 & self.west_mask) & self.mask
        return clone

    def __shift_nw(self) -> Bitboard:
        clone = copy(self)
        clone.bits = (self.bits >> self.size+1 & self.east_mask) & self.mask
        return clone

    def __shift_se(self) -> Bitboard:
        clone = copy(self)
        clone.bits = (self.bits << self.size+1 & self.west_mask) & self.mask
        return clone

    def __shift_sw(self) -> Bitboard:
        clone = copy(self)
        clone.bits = (self.bits << self.size-1 & self.east_mask) & self.mask
        return clone

    def __coords_to_bit_idx(self, x: int, y: int) -> int:
        return y * self.size + x

    def __check_bit_idx_is_legal(self, bit_idx: int) -> None:
        if not 0 <= bit_idx < (self.size * self.size):
            # avoiding out-of-bound access
            raise IndexError

    def __and__(self, o: Bitboard) -> Bitboard:
        r = copy(self)
        return Bitboard(self.size, r.bits & o.bits)

    def __or__(self, o: Bitboard) -> Bitboard:
        r = copy(self)
        return Bitboard(self.size, r.bits | o.bits)

    def __xor__(self, o: Bitboard) -> Bitboard:
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
