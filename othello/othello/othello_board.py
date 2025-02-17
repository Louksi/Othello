"""
Everything related to the actual board of Othello.
"""
from enum import Enum
from string import ascii_lowercase


from othello.bitboard import Bitboard, Direction


class Color(Enum):
    """
    Enum with the possibilities for a case as well as their string representation.
    """
    BLACK = "X"
    WHITE = "O"
    EMPTY = "_"


class BoardSize(Enum):
    """
    Available board sizes.
    """
    SIX_BY_SIX = 6
    EIGHT_BY_EIGHT = 8
    TEN_BY_TEN = 10
    TWELVE_BY_TWELVE = 12


class OthelloBoard:
    """
    Implementation of an othello board that uses Bitboards
    """

    def __init__(self, size: BoardSize):
        """
        :param size: The size of the Bitboard from the enum `BoardSize`
        :param type: BoardSize
        """
        self.size = size
        self.black = Bitboard(size.value)
        self.white = Bitboard(size.value)
        # we copy a mask from one of our bitboards as they are equals and immutables
        self.mask = self.black.mask
        self.__init_board()

    def __init_board(self):
        """
        Initialize the starting position of the Othello board.

        This method sets up the initial four pieces in the center of the board,
        with two black pieces and two white pieces placed diagonally from each other.
        """

        self.white.set(self.size.value // 2 - 1,
                       self.size.value // 2 - 1, True)
        self.white.set(self.size.value // 2, self.size.value // 2, True)
        self.black.set(self.size.value//2-1, self.size.value//2, True)
        self.black.set(self.size.value//2, self.size.value//2-1, True)

    def line_cap_move(self, current_player: Color) -> Bitboard:
        """
        Returns a bitboard of the possibles plays for `current_player`

        :param current_player: The player trying to do the capture
        :param type: Color
        :returns: A Bitboard of the possible capture moves for player `current_player`
        """
        bits_p = self.black if current_player is Color.BLACK else self.white
        bits_o = self.white if current_player is Color.BLACK else self.black
        moves = Bitboard(self.size.value)
        for shift_dir in Direction:
            candidates = bits_o & (bits_p.shift(shift_dir))
            while candidates.bits != 0:
                moves |= self.__empty_mask() & candidates.shift(shift_dir)
                candidates = bits_o & candidates.shift(shift_dir)
        return moves

    def line_cap(self, x_coord: int, y_coord: int, current_player: Color) -> Bitboard:
        """
        Returns the result of a capture. Does not check if the capture is legal.
        Do the check beforehand if you intend to use this function.

        :param x_coord: the x coordinate of the play
        :param type: int
        :param y_coord: the y coordinate of the play
        :param type: int
        :param current_player: the player making the move
        :param type: Color
        :returns: The bitboard of the captured bits.
        :rtype: Bitboard
        """
        bits_p = self.black if current_player is Color.BLACK else self.white
        bits_o = self.white if current_player is Color.BLACK else self.black
        position = Bitboard(self.size.value)
        position.set(x_coord, y_coord, True)
        cap_mask = Bitboard(self.size.value, bits=position.bits)
        for shift_dir in Direction:
            direction_mask = Bitboard(self.size.value, bits=position.bits)
            direction_ptr = Bitboard(self.size.value, bits=position.bits)

            while direction_ptr.bits != 0:
                direction_ptr = direction_ptr.shift(shift_dir)
                if (direction_ptr & bits_o).bits:
                    direction_mask |= direction_ptr
                elif (direction_ptr & bits_p).bits:
                    cap_mask |= direction_mask
                    break
                else:
                    break

        return cap_mask

    def __empty_mask(self) -> Bitboard:
        """
        Compute a bitboard that represents all the empty squares on the board.

        The empty mask is the XOR of the white and black bitboards with the mask
        of the board. This is equivalent to finding all the squares that have not
        been set to either white or black.

        :return: A bitboard representing all the empty squares on the board.
        :rtype: Bitboard
        """
        return Bitboard(self.size.value, (self.white.bits | self.black.bits) ^ self.mask)

    def __str__(self) -> str:
        """
        Return a string representation of the board in the standard algebraic notation

        Each rank is labeled with a number and each file is labeled with a letter.
        Black pions are represented by 'X', white pions are represented by 'O',
        and empty squares are represented by '_'.

        :return: A string representation of the board in the standard algebraic notation
        :rtype: str
        """
        rez = "  "

        rez += " ".join([ascii_lowercase[letter_idx]
                        for letter_idx in range(self.size.value)])
        for y_coord in range(self.size.value):
            rez += "\n"
            for x_coord in range(self.size.value):
                has_black = self.black.get(x_coord, y_coord)
                has_white = self.white.get(x_coord, y_coord)
                if x_coord == 0:
                    rez += str(y_coord+1) + " "
                if has_black:
                    rez += Color.BLACK.value
                elif has_white:
                    rez += Color.WHITE.value
                else:
                    rez += Color.EMPTY.value
                if x_coord < self.size.value-1:
                    rez += " "
        return rez
