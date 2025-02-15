from othello.othello_board import OthelloBoard, BoardSize, Color
import othello.parser as parser
from othello.blitzTimer import BlitzTimer


class BlitzMode:
    def __init__(self, board_size: BoardSize):
        """
        Initialize the BlitzMode with the given board size.

        This sets up a new Othello game in Blitz mode, initializing the board,
        timer, and setting the starting player to black.

        :param board_size: The size of the Othello board.
        :type board_size: BoardSize
        """

        if parser.GameMode.BLITZ:
            self.board_size = board_size
            self.board = OthelloBoard(self.board_size)
            self.blitz_timer = BlitzTimer(parser.DEFAULT_BLITZ_TIME)
            self.current_player = Color.BLACK
            self.blitz_timer.startTimer('black')

    def switch_turn(self):
        # Check if time is up for current player
        """
        Switch the current player and start the timer for the next player.

        Returns:
            bool: True if the game is still ongoing, False if a player has won.
        """
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
        """
        Play a move at the given coordinates.

        This applies the current player's move at the given coordinates and
        switches to the other player.

        :param x: The x coordinate of the move.
        :param y: The y coordinate of the move.
        :type x: int
        :type y: int
        """
        self.board.line_cap(x, y, self.current_player)

    def __str__(self):
        """
        Return a string representation of the board.

        :return: A string representation of the board.
        :rtype: str
        """

        return str(self.board)
