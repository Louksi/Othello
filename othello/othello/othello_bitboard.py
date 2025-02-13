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
        """
        Initialize an OthelloBitboard with the given board size.

        This sets up a bitboard for both black and white players, and initializes
        the mask used for board operations. The starting board configuration 
        is set with the initial pieces in place.

        :param size: The size of the Othello board.
        :type size: BoardSize
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
        Compute the legal moves of the current player with the line capture algorithm.

        The line capture algorithm iterates over all the directions of the board,
        and for each direction, it looks for a sequence of opponent's pieces
        that can be captured by the current player. The legal moves are the
        squares at the end of each of these sequences.

        :param current_player: The color of the current player.
        :type current_player: Color
        :return: A bitboard representing the legal moves of the current player.
        :rtype: Bitboard
        """
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
        """
        Compute the capture mask for the given position and player.

        The capture mask is a bitboard that contains all the pieces that can be
        captured by the current player when placing a piece at the given position.
        The capture mask is computed by iterating over all the directions of the
        board and looking for a sequence of opponent's pieces that can be captured
        by the current player. The capture mask is the union of all the squares at
        the end of each of these sequences.

        :param x: The x coordinate of the position.
        :type x: int
        :param y: The y coordinate of the position.
        :type y: int
        :param current_player: The color of the current player.
        :type current_player: Color
        :return: A bitboard representing the capture mask of the current player.
        :rtype: Bitboard
        """
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
        Return a string representation of the board, with the x and y dimension
        shown. "X" for black, "O" for white, and " " for empty squares.
        """
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
