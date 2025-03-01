"""
This modules contains utilities used for loading an OthelloBoard from a save
"""
import re
from othello.bitboard import Bitboard
from othello.othello_board import BoardSize, Color, IllegalMoveException, OthelloBoard


class BoardParserException(Exception):
    """
    Thrown on parsing error, contains a custom message as well as the line where it happened
    """

    def __init__(self, msg: str, line: int):
        super().__init__(f"{msg} AT LINE {line}")


class BoardParser:
    """
    Takes a board at initialization and allows for retrieving an OthelloBoard matching
    the state of the board save str representation.
    """

    def __init__(self, raw_save: str):
        self.__buffer = raw_save.split("\n")
        self.__x = 0
        self.__y = 0
        self.__case_values = tuple(c.value for c in Color)

    def parse(self) -> OthelloBoard:
        """
        Parses the board given at init time and returns an OthelloBoard configured accordingly.
        """
        board = self.__parse_board()
        maybe_computed_board = self.__parse_history(board)
        if maybe_computed_board is not None:
            board = maybe_computed_board

        return board

    def __parse_board(self):
        color = None
        # first we need to find the color.
        self.__skip_newlines()
        if self.__eof():
            raise BoardParserException(
                "trying to parse an empty board", self.__y)
        if self.__current() not in (Color.BLACK.value, Color.WHITE.value):
            raise BoardParserException("expected to find color", self.__y)
        color = Color.BLACK if self.__current() == Color.BLACK.value else Color.WHITE
        # then we need to find the start of the board
        self.__skip_newlines()
        self.__x = 0
        self.__next_line()
        # we pre-parse the first line to find the supposed size of the board
        if self.__eof():
            raise BoardParserException("reached end of file", self.__y)
        board_size = self.__find_board_size()
        if board_size not in (bs.value for bs in BoardSize):
            raise BoardParserException("illegal board size value", self.__y)
        # and now we generate the two masks and add black and white pieces line by line
        black_mask = Bitboard(board_size)
        white_mask = Bitboard(board_size)
        for board_y in range(board_size):
            if self.__eof():
                raise BoardParserException(
                    "reached end of file before finished parsing", self.__y)
            self.__skip_newlines()
            (line_black_mask, line_white_mask) = self.__line_mask(
                board_y, board_size)
            black_mask |= line_black_mask
            white_mask |= line_white_mask
            if board_y < board_size - 1:
                self.__next_line()
        return OthelloBoard(BoardSize.from_value(board_size),
                            black=black_mask, white=white_mask, current_player=color)

    def __parse_history(self, board: OthelloBoard):
        self.__skip_newlines()
        if self.__eof():
            return None
        str_board_max_column = chr(ord('a') + board.size.value)
        str_board_max_line = board.size.value + 1
        play_regex = fr"(([a-{str_board_max_column}][1-{str_board_max_line}])|(-1-1))"
        line_regex = fr"(\d+)\. X {play_regex}( O {play_regex})?"
        line_regex_compiled = re.compile(line_regex)

        computed_board = OthelloBoard(board.size)
        while not self.__eof():
            self.__parse_history_turn(computed_board, line_regex_compiled)
            self.__skip_newlines()
        return computed_board

    def __parse_history_turn(self, board: OthelloBoard, line_regex):
        line = str()
        while not self.__eol():
            line += self.__current()
            self.__next_char()
        matches = line_regex.match(line)

        if matches is None:
            raise BoardParserException(
                f"incorrect line format: \"{line}\"", self.__y)
        turn_id = int(matches.group(1))
        black_play = matches.group(2)
        white_play = matches.group(6)
        if turn_id != board.get_turn_id():
            raise BoardParserException(
                "incorrect turn number in history", self.__y)
        try:
            move = self.__parse_move(black_play)
            board.play(move[0], move[1])
        except IllegalMoveException as exc:
            raise BoardParserException(
                f"black move {black_play} is illegal ({exc})", self.__y)

        if white_play is not None:
            try:
                move = self.__parse_move(white_play)
                board.play(move[0], move[1])
            except IllegalMoveException as exc:
                print(board)
                raise BoardParserException(
                    f"white move {white_play} is illegal ({exc})", self.__y)

    def __parse_move(self, move: str) -> tuple[int, int]:
        if move == "-1-1":
            return (-1, -1)
        move_x_coord = ord(move[0]) - ord('a')
        move_y_coord = int(move[1:])-1
        return (move_x_coord, move_y_coord)

    def __next_char(self):
        if self.__eol():
            self.__y += 1
            self.__x = 0
        else:
            self.__x += 1

    def __next_line(self):
        if not self.__eof():
            self.__y += 1
            self.__x = 0
        else:
            raise BoardParserException("already reached EOF", self.__y)

    def __eol(self, peek_cursor=0):
        return self.__x+peek_cursor == len(self.__buffer[self.__y])\
            or self.__peek(peek_cursor) == "#"

    def __eof(self):
        return self.__y >= len(self.__buffer) or (self.__eol() and self.__y >= len(self.__buffer)-1)

    def __line_mask(self, board_y: int, board_size: int) -> tuple[Bitboard, Bitboard]:
        black_mask = Bitboard(board_size)
        white_mask = Bitboard(board_size)
        case_cursor = 0
        while not self.__eol():
            peek_value = self.__current()
            if peek_value in self.__case_values:
                if peek_value == Color.BLACK.value:
                    black_mask.set(case_cursor, board_y, True)
                elif peek_value == Color.WHITE.value:
                    white_mask.set(case_cursor, board_y, True)
                case_cursor += 1
            elif peek_value != " ":
                raise BoardParserException(
                    f"expected to find either a case or a space, found {peek_value}", self.__y)
            self.__next_char()
        if case_cursor != board_size:
            raise BoardParserException(
                f"Line of size {case_cursor} where it should have been {board_size}", self.__y)
        return (black_mask, white_mask)

    def __find_board_size(self) -> int:
        board_size = 0
        peek_cursor = 0
        while not self.__eol(peek_cursor):
            peek_value = self.__peek(peek_cursor)
            if peek_value in self.__case_values:
                board_size += 1
            elif peek_value != " ":
                raise BoardParserException(
                    f"expected to find either a case or a space, found {peek_value}", self.__y)
            peek_cursor += 1

        return board_size

    def __peek(self, n_to_peek: int) -> str:
        return self.__buffer[self.__y][self.__x+n_to_peek]

    def __skip_spaces(self):
        while not self.__eol() and self.__current() == " ":
            self.__next_char()

    def __skip_newlines(self):
        self.__skip_spaces()
        while not self.__eof() and self.__eol():
            self.__next_line()
            self.__x = 0
            self.__skip_spaces()

    def __current(self) -> str:
        return self.__buffer[self.__y][self.__x]
