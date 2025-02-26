import sys
import othello.parser as parser
from othello.othello_board import BoardSize, OthelloBoard, Color
from othello.blitz_timer import BlitzTimer


class NormalGame:
    def __init__(self, board_size: BoardSize = BoardSize.EIGHT_BY_EIGHT):
        """
        Initialize the NormalGame with the given board size.

        This sets up a new Othello game in Normal mode, initializing the board
        and setting the starting player to black.

        :param board_size: The size of the Othello board.
        :type board_size: BoardSize
        """
        if isinstance(board_size, int):
            board_size = BoardSize(board_size)
        self.board = OthelloBoard(board_size)
        self.current_player = Color.BLACK
        self.no_black_move = False
        self.no_white_move = False

    def display_board(self):
        """
        Display the current state of the board and indicate the current player's turn.

        This function prints a string representation of the Othello board and 
        indicates which player's turn it is by displaying the player's name 
        and corresponding symbol.
        """

        print(str(self.board))
        print(f"\n{self.current_player.name}'s turn ({self.current_player.value})")

    def get_possible_moves(self):
        """
        Returns a bitboard of the possible capture moves for the current player.

        This function queries the board for the possible capture moves for the
        current player and returns them as a bitboard.

        :return: A Bitboard of the possible capture moves for the current player.
        :rtype: Bitboard
        """
        return self.board.line_cap_move(self.current_player)

    def check_game_over(self, possible_moves):
        """
        Checks if the game is over by seeing if there are any valid moves
        remaining for the current player. If there are no valid moves for
        the current player, the game is over and the other player wins. If
        there are no valid moves for both players, the game is over and
        the game state is printed.

        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type possible_moves: Bitboard
        :return: True if the game is over, False otherwise.
        :rtype: bool
        """
        if possible_moves.bits == 0:
            if self.current_player == Color.BLACK:
                self.no_black_move = True
            if self.current_player == Color.WHITE:
                self.no_white_move = True

            if self.no_black_move and self.no_white_move:
                print("No valid moves for both players. Game over.")
                return True

            print(
                f"No valid moves for {self.current_player.name}. Skipping turn.")
            return False

        print(self.no_black_move, self.no_white_move)
        if self.board.black.popcount() + self.board.white.popcount() == self.board.size.value * self.board.size.value:
            if self.board.black.popcount() > self.board.white.popcount():
                print("Black wins!")
                return True
            if self.board.black.popcount() < self.board.white.popcount():
                print("White wins!")
                return True
        return False

    def display_possible_moves(self, possible_moves):
        """
        Prints the possible moves in a human-readable format.

        The function takes a bitboard of possible moves and prints it
        in a human-readable format. The format is a series of letters
        and numbers, where each letter corresponds to a column and
        each number corresponds to a row. For example, the coordinate
        "a1" would correspond to the top-left corner of the board.

        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type possible_moves: Bitboard
        """
        print("Possible moves: ")
        for y in range(self.board.size.value):
            for x in range(self.board.size.value):
                if possible_moves.get(x, y):
                    print(f"{chr(ord('a')+x)}{y+1}", end=" ")
        print()

    def get_player_move(self):
        """
        Asks the user to enter a move and returns the coordinates of the move.

        The function asks the user to enter a move in the format "a1" and
        returns the coordinates of the move as a tuple of (x, y). If the
        user enters an invalid move, the function prints an error message
        and returns None.

        :return: A tuple of (x, y) coordinates of the move.
        :rtype: tuple or None
        """
        move = input("Enter your move: ").strip().lower()
        if len(move) < 2 or move[0] not in "abcdef"[:self.board.size.value] or not move[1:].isdigit():
            print("Invalid move format. Try again.")
            return None
        x_coord = ord(move[0]) - ord('a')
        y_coord = int(move[1]) - 1
        return x_coord, y_coord

    def process_move(self, x_coord, y_coord, possible_moves):
        """
        Processes a move by the current player at the given coordinates.

        This function checks if the move at the specified coordinates is legal by
        consulting the possible moves bitboard. If the move is legal, it plays the
        move on the board. If the move is not legal, it prints an error message
        indicating the move is invalid.

        :param x_coord: The x coordinate of the move.
        :param y_coord: The y coordinate of the move.
        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type x_coord: int
        :type y_coord: int
        :type possible_moves: Bitboard
        :return: True if the move is successfully processed, False if the move is invalid.
        :rtype: bool
        """

        if not possible_moves.get(x_coord, y_coord):
            print("Invalid move. Not a legal play. Try again.")
            return False
        self.board.play(x_coord, y_coord)
        return True

    def switch_player(self):
        """
        Switches the current player.

        This function toggles the current player between black and white.
        It does not return any value.
        """

        self.current_player = (
            Color.WHITE if self.current_player == Color.BLACK else Color.BLACK
        )

    def play(self):
        """
        Main game loop.

        This function implements the main game loop of Othello. It is an infinite loop
        that continues until the game is over. The loop consists of the following steps:

        1. Display the current state of the board.
        2. Compute the possible moves for the current player.
        3. If the game is over, continue to the next iteration.
        4. Display the possible moves.
        5. Get a move from the current player.
        6. If the move is invalid, continue to the next iteration.
        7. Process the move by playing it on the board.
        8. Switch the current player.

        :return: None
        """
        while True:
            self.display_board()
            possible_moves = self.get_possible_moves()

            if self.check_game_over(possible_moves):
                continue

            self.display_possible_moves(possible_moves)
            move = self.get_player_move()
            if move is None:
                continue

            x_coord, y_coord = move
            if not self.process_move(x_coord, y_coord, possible_moves):
                continue

            self.switch_player()


class BlitzGame(NormalGame):
    def __init__(self, board_size: BoardSize = BoardSize.EIGHT_BY_EIGHT, time: int = None):
        """
        Initialize the BlitzGame with the given board size and time limit.

        This sets up a new Othello game in Blitz mode, initializing the board,
        timer, and setting the starting player to black. The Blitz timer is
        started for the black player.

        :param board_size: The size of the Othello board.
        :type board_size: BoardSize
        :param time: The time limit for each player in minutes. Defaults to the
                    parser's DEFAULT_BLITZ_TIME if not specified.
        :type time: int, optional
        """

        super().__init__(BoardSize(board_size) if isinstance(board_size, int) else board_size)
        self.blitz_timer = BlitzTimer(
            time if time is not None else parser.DEFAULT_BLITZ_TIME)
        self.blitz_timer.start_timer('black')

    def switch_player(self):
        """
        Switches the current player, updating the Blitz timer for the next player.

        If a player's time has expired, the game is over and the winner is printed.
        Otherwise, the Blitz timer is updated by switching the current player and
        starting the timer for the new player.
        """
        if self.blitz_timer.is_time_up('black'):
            print("Black's time is up! White wins!")
            sys.exit(0)
        elif self.blitz_timer.is_time_up('white'):
            print("White's time is up! Black wins!")
            sys.exit(0)

        super().switch_player()  # Switch player as normal
        next_player = 'white' if self.current_player == Color.WHITE else 'black'
        self.blitz_timer.change_player(next_player)

    def display_time(self):
        """
        Prints the remaining time for both players.

        This method prints the formatted string returned by BlitzTimer.display_time,
        which shows the remaining time for both black and white players in minutes and
        seconds.
        """
        print(self.blitz_timer.display_time())

    def check_game_over(self, possible_moves):
        """
        Checks if the game is over by verifying if a player's time has expired or
        if there are no valid moves left for the current player.

        This function first checks if the blitz timer has run out for either player,
        declaring the other player as the winner if so. If both players still have
        time remaining, it checks for valid moves using the parent class's method.

        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type possible_moves: Bitboard
        :return: True if the game is over, False otherwise.
        :rtype: bool
        """

        if self.blitz_timer.is_time_up('black'):
            print("Black's time is up! White wins!")
            sys.exit(0)
        elif self.blitz_timer.is_time_up('white'):
            print("White's time is up! Black wins!")
            sys.exit(0)

        return super().check_game_over(possible_moves)

    def play(self):
        """
        Main game loop for Blitz mode.

        This function implements the main game loop for Blitz mode, which is
        similar to the main game loop for Normal mode. However, Blitz mode
        includes a time limit for each player, and the game ends when either
        player's time runs out or when there are no valid moves left for the
        current player.

        The loop consists of the following steps:

        1. Display the current state of the board.
        2. Compute the possible moves for the current player.
        3. If the game is over, continue to the next iteration.
        4. Display the possible moves.
        5. Get a move from the current player.
        6. If the move is invalid, continue to the next iteration.
        7. Process the move by playing it on the board.
        8. Switch the current player.
        9. Print the remaining time for both players.
        """
        while True:
            self.display_board()
            possible_moves = self.get_possible_moves()
            if self.check_game_over(possible_moves):
                continue

            self.display_possible_moves(possible_moves)
            move = self.get_player_move()
            if move is None:
                continue

            x_coord, y_coord = move
            if not self.process_move(x_coord, y_coord, possible_moves):
                continue

            self.switch_player()
            print()
            self.display_time()
