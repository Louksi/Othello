from othello.othello_board import OthelloBoard, BoardSize, Color
import othello.parser as parser
from othello.blitz_timer import BlitzTimer
from othello.normal_game import print_board, get_valid_move, print_possible_moves, is_game_over


class BlitzMode:
    def __init__(self, board_size: BoardSize = BoardSize.EIGHT_BY_EIGHT, time: int = None):
        """
        Initialize the BlitzMode with optional board size and time.

        :param board_size: The size of the Othello board (default: 8x8).
        :type board_size: BoardSize
        :param time: The time for blitz mode in seconds (default: parser.DEFAULT_BLITZ_TIME).
        :type time: int, optional
        """
        if parser.GameMode.BLITZ:
            self.board_size = BoardSize(board_size) if isinstance(board_size, int) else board_size
            self.board = OthelloBoard(self.board_size)
            self.blitz_timer = BlitzTimer(time if time is not None else parser.DEFAULT_BLITZ_TIME)
            self.current_player = Color.BLACK
            self.blitz_timer.start_timer('black')


    def switch_turn(self):
        """
        Switch the current player and start the timer for the next player.

        Returns:
            bool: True if the game is still ongoing, False if a player has won.
        """
        if self.blitz_timer.is_time_up('black'):
            print("Black's time is up! White wins!")
            return False
        elif self.blitz_timer.is_time_up('white'):
            print("White's time is up! Black wins!")
            return False

        # Switch current player
        self.current_player = Color.WHITE if self.current_player == Color.BLACK else Color.BLACK
        next_player = 'white' if self.current_player == Color.WHITE else 'black'
        self.blitz_timer.change_player(next_player)
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
        self.board.play(x, y)
        self.switch_turn()

    def __str__(self):
        """
        Return a string representation of the board.

        :return: A string representation of the board.
        :rtype: str
        """

        return str(self.board)

    def blitz_moves(self):
        return self.board.line_cap_move(self.current_player)

    def print_time(self):   
        print(self.blitz_timer.display_time())

    def is_game_over(self):
        return self.blitz_timer.is_time_up('black') or self.blitz_timer.is_time_up('white') or is_game_over(self.board,self.current_player)
    
    
def blitz_play(size, time):
    game = BlitzMode(size, time)
    while True:
        print_board(game)
        print(f"\n{game.current_player.name}'s turn ({game.current_player.value})")
        possible_moves = game.blitz_moves()

        if game.is_game_over():
            break

        
        print_possible_moves(possible_moves, game.board.size.value)
        
        x_coord, y_coord = get_valid_move(possible_moves, game.board.size.value)
        game.play_move(x_coord, y_coord)

        game.print_time()

        

        
    