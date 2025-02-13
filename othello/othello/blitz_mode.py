from othello.othello_bitboard import OthelloBitboard, BoardSize, Color
import othello.parser as parser
from othello.blitzTimer import BlitzTimer


class BlitzMode:
    def __init__(self, board_size: BoardSize):
        if parser.GameMode.BLITZ:
            self.board_size = board_size
            self.board = OthelloBitboard(self.board_size)
            self.blitz_timer = BlitzTimer(parser.DEFAULT_BLITZ_TIME)
            self.current_player = Color.BLACK
            self.blitz_timer.startTimer('black')

    def switch_turn(self):
        # Check if time is up for current player
        if self.blitz_timer.isTimeUp('black'):
            print("Black's time is up! White wins!")
            return False
        elif self.blitz_timer.isTimeUp('white'):
            print("White's time is up! Black wins!")
            return False

        # Switch current player
        self.current_player = Color.WHITE if self.current_player == Color.BLACK else Color.BLACK
        next_player = 'white' if self.current_player == Color.WHITE else 'black'
        self.blitz_timer.changePlayer(next_player)
        return True

    def play_move(self, x: int, y: int):
        self.board.line_cap(x, y, self.current_player)

    def __str__(self):
        return str(self.board)
