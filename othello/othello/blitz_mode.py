from othello.othello_bitboard import OthelloBitboard, BoardSize
import othello.parser as parser


class BlitzMode:
    def __init__(self, board_size: BoardSize):
        if parser.GameMode.BLITZ:
            self.board_size = board_size
            self.board = OthelloBitboard(self.board_size)
            self.time_limit = parser.DEFAULT_BLITZ_TIME

    def __str__(self):
        return OthelloBitboard.__str__(self.board)
