from enum import Enum
from string import ascii_lowercase


from othello.bitboard import Bitboard, Direction


class Color(Enum):
    BLACK = "X"
    WHITE = "O"


class BoardSize(Enum):
    SIX_BY_SIX = 6
    EIGHT_BY_EIGHT = 8
    TEN_BY_TEN = 10
    TWELVE_BY_TWELVE = 12


class OthelloBitboard:
    def __init__(self, size: BoardSize):
        self.size = size
        self.black = Bitboard(size.value)
        self.white = Bitboard(size.value)
        # we copy a mask from one of our bitboards as they are equals and immutables
        self.mask = self.black.mask
        self.__init_board()

    def __init_board(self):
        self.white.set(self.size.value // 2 - 1,
                       self.size.value // 2 - 1, True)
        self.white.set(self.size.value // 2, self.size.value // 2, True)
        self.black.set(self.size.value//2-1, self.size.value//2, True)
        self.black.set(self.size.value//2, self.size.value//2-1, True)

    def line_cap_move(self, current_player: Color) -> Bitboard:
        bits_p = self.black if current_player is Color.BLACK else self.white
        bits_o = self.white if current_player is Color.BLACK else self.black
        moves = Bitboard(self.size.value)
        for d in Direction:
            candidates = bits_o & (bits_p.shift(d))
            while candidates.bits != 0:
                moves |= self.__empty_mask() & candidates.shift(d)
                candidates = bits_o & candidates.shift(d)
        return moves

    def line_cap(self, x: int, y: int, current_player: Color) -> Bitboard:
        bits_p = self.black if current_player is Color.BLACK else self.white
        bits_o = self.white if current_player is Color.BLACK else self.black
        cap_mask = Bitboard(self.size.value)
        cap_mask.set(x, y, True)
        for d in Direction:
            direction_mask = Bitboard(self.size.value, bits=cap_mask.bits)
            direction_ptr = Bitboard(self.size.value, bits=cap_mask.bits)
            while direction_ptr.bits != 0:
                direction_ptr = direction_ptr.shift(d)
                if (direction_ptr & bits_o).bits:
                    direction_mask |= direction_ptr
                elif (direction_ptr & bits_p).bits:
                    cap_mask |= direction_mask
                    break

        return cap_mask

    def __empty_mask(self) -> Bitboard:
        return Bitboard(self.size.value, (self.white.bits | self.black.bits) ^ self.mask)

    def __str__(self) -> str:
        rez = " "

        rez += " ".join([ascii_lowercase[letter_idx]
                        for letter_idx in range(self.size.value)])
        for y in range(self.size.value):
            rez += "\n"
            for x in range(self.size.value):
                has_black = self.black.get(x, y)
                has_white = self.white.get(x, y)
                if x == 0:
                    rez += str(y)
                if has_black:
                    # ENUM
                    rez += "X"
                elif has_white:
                    rez += "O"
                else:
                    rez += " "
                rez += " "
        return rez
