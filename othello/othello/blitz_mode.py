import time
from othello.othello_bitboard import OthelloBitboard, BoardSize, Color
import othello.parser as parser


class BlitzMode:
    def __init__(self, board_size: BoardSize):
        if parser.GameMode.BLITZ:
            self.board_size = board_size
            self.board = OthelloBitboard(self.board_size)
            # Total time for each player in seconds
            self.time_limit = parser.DEFAULT_BLITZ_TIME
            self.time_black = self.time_limit
            self.time_white = self.time_limit
            self.current_player = Color.BLACK
            self.start_time = time.time()

    def switch_turn(self):
        # Calculate elapsed time
        elapsed_time = time.time() - self.start_time
        if self.current_player == Color.BLACK:
            self.time_black -= elapsed_time
            if self.time_black <= 0:
                print("Black's time is up! White wins!")
                return False
        else:
            self.time_white -= elapsed_time
            if self.time_white <= 0:
                print("White's time is up! Black wins!")
                return False

        # Switch player and restart timer
        self.current_player = Color.WHITE if self.current_player == Color.BLACK else Color.BLACK
        self.start_time = time.time()
        return True

    def play_move(self, x: int, y: int):
        # Validate and play move
        legal_moves = self.board.line_cap_move(self.current_player)
        if legal_moves.get(x, y):
            caps = self.board.line_cap(x, y, self.current_player)
            bits_current = self.board.black if self.current_player == Color.BLACK else self.board.white
            bits_opponent = self.board.white if self.current_player == Color.BLACK else self.board.black

            # Apply the move and flip the discs
            bits_current.set(x, y, True)
            bits_current.bits |= caps.bits
            bits_opponent.bits &= ~caps.bits

            # Switch turn and check for timeout
            return self.switch_turn()
        else:
            print("Invalid move. Try again.")
            return True

    def display_time(self):
        print(
            f"Time remaining - Black: {int(self.time_black)}s | White: {int(self.time_white)}s")

    def __str__(self):
        return str(self.board)
