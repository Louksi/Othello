"""Game Modes for Othello """
# pylint: disable=locally-disabled, multiple-statements, line-too-long, import-error, no-name-in-module

import logging
import sys

import othello.parser as parser
import othello.logger as log
from othello.command_parser import CommandParser, CommandKind, CommandParserException
from othello.board_parser import BoardParser
from othello.parser import DEFAULT_BLITZ_TIME
from othello.config import save_board_state_history
from othello.othello_board import BoardSize, OthelloBoard, Color
from othello.blitz_timer import BlitzTimer
from othello.ai_features import find_best_move


logger = logging.getLogger("Othello")


class NormalGame:
    '''
    A class representing a Normal Othello game.
    '''

    def __init__(self, filename=str, board_size: BoardSize = BoardSize.EIGHT_BY_EIGHT):
        """
        Initialize the NormalGame with the given board size.

        This sets up a new Othello game in Normal mode, initializing the board
        and setting the starting player to black.

        :param board_size: The size of the Othello board.
        :type board_size: BoardSize
        """
        logger.debug(
            "Entering game initialization function from game_modes.py, "
            "with parameter board size: %s", board_size)

        if filename is None:
            if isinstance(board_size, int):
                board_size = BoardSize(board_size)
                self.board = OthelloBoard(board_size)
                self.board_size = board_size
                self.current_player = Color.BLACK

            else:
                self.board = OthelloBoard(board_size)
                self.board_size = board_size.value
                self.current_player = Color.BLACK
        else:
            logger.debug("Loading game from file: %s.", filename)
            try:
                with open(f"{filename}", "r") as file:
                    file_content = file.read()

                parsed_board = BoardParser(file_content).parse()
                self.current_player = parsed_board.current_player
                self.board = parsed_board
                self.board_size = parsed_board.size
            except Exception as err:
                log.log_error_message(
                    err, context=("Failed to load game from file: %s.", filename))
                raise

        self.no_black_move = False
        self.no_white_move = False
        logger.debug(
            " NormalGame initialized with board_size: %s, current_player: %s.",
            self.board_size, self.current_player)

    def display_board(self):
        """
        Display the current state of the board and indicate the current player's turn.

        This function prints a string representation of the Othello board and
        indicates which player's turn it is by displaying the player's name
        and corresponding symbol.
        """
        logger.debug("Entering display_board function from game_modes.py.")
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
        logger.debug(
            "Entering get_possible_moves function from game_modes.py.")
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
        logger.debug("Entering check_game_over function from game_modes.py.")
        if possible_moves.bits == 0:
            if self.current_player == Color.BLACK:
                self.no_black_move = True
                logger.debug(
                    "   No moves available for %s player.", self.current_player)
            if self.current_player == Color.WHITE:
                self.no_white_move = True
                logger.debug(
                    "   No moves available for %s player.", self.current_player)

            if self.no_black_move and self.no_white_move:
                logger.debug("   No valid moves for both players. Game over.")
                print("No valid moves for both players. Game over.")
                return True

            logger.debug(
                "   No valid moves for %s. Skipping turn.", self.current_player)
            print(
                "No valid moves for %s. Skipping turn.", self.current_player.name)
            return False

        total_moves = self.board.black.popcount() + self.board.white.popcount()
        if total_moves == self.board.size.value * self.board.size.value:
            logger.debug(
                "   Final score - Black: %s, White: %s", self.board.black.popcount(), self.board.white.popcount())
            if self.board.black.popcount() > self.board.white.popcount():
                logger.debug("   Black wins.")
                print("Black wins!")
                return True
            if self.board.black.popcount() < self.board.white.popcount():
                logger.debug("   White wins.")
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
        logger.debug(
            "Entering display_possible_moves function from game_modes.py,"
            " with parameter possible_moves.")
        logger.debug("   Available moves:\n %s", str(possible_moves))
        print("Possible moves: ")
        for y in range(self.board.size.value):
            for x in range(self.board.size.value):
                if possible_moves.get(x, y):
                    print(f"{chr(ord('a')+x)}{y+1}", end=" ")
        print()

    def get_player_move(self):
        """
        Prompts the current player to enter their move.

        This function reads the player's move input in the format of a letter
        followed by a number (e.g., "a1"). It converts the input into x and y
        coordinates, where 'a' corresponds to 0 and '1' corresponds to 0, and
        returns these coordinates.

        :return: A tuple containing the x and y coordinates of the move.
        :rtype: tuple[int, int]
        """
        logger.debug("Entering get_player_move function from game_modes.py.")
        move = input("Enter your move: ").strip().lower()
        logger.debug("   Player entered: %s", move)

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
        logger.debug(
            "Entering process_move function from game_modes.py, with parameters x_coord:"
            "%s, y_coord: %s, and possible_moves.", x_coord, y_coord)
        if not possible_moves.get(x_coord, y_coord):
            logger.debug("   The move is not legal to play")
            print("Invalid move. Not a legal play. Try again.")
            return False
        logger.debug("   Move (%s, %s) is legal, playing.", x_coord, y_coord)
        self.board.play(x_coord, y_coord)
        return True

    def switch_player(self):
        """
        Switches the current player.

        This function toggles the current player between black and white.
        It does not return any value.
        """
        logger.debug("Entering switch_player function from game_modes.py.")
        self.current_player = (
            Color.WHITE if self.current_player == Color.BLACK else Color.BLACK
        )

    def play(self):
        """
        Starts the game loop for Normal mode.

        This function starts the main game loop. The loop begins by displaying
        the current state of the board. It then prompts the current player for
        input. The input is parsed into a CommandType, which is a tuple of a
        CommandKind and some relevant information for that kind. The function
        then processes the command based on the kind.

        The loop continues until the game is over, or the user quits.

        :return: None
        """
        logger.debug("Entering play function from game_modes.py.")
        parser = CommandParser(board_size=self.board.size.value)

        while True:
            self.display_board()
            possible_moves = self.get_possible_moves()

            if self.check_game_over(possible_moves):
                # If game over, restart the loop (display final board state)
                continue

            self.display_possible_moves(possible_moves)
            command_str = input("Enter your move or command: ").strip()
            logger.debug("   Player input: '%s'.", command_str)

            try:
                command_kind, *args = parser.parse_str(command_str)

                if command_kind == CommandKind.PLAY_MOVE:
                    play_command = args[0]
                    x_coord, y_coord = play_command.x_coord, play_command.y_coord
                    logger.debug(
                        "   Play move command at (%s, %s).", x_coord, y_coord)

                    if not self.process_move(x_coord, y_coord, possible_moves):
                        continue  # Invalid move, prompt player again

                    self.switch_player()

                else:
                    match command_kind:
                        case CommandKind.HELP:
                            logger.debug(
                                "   Executing %s command.", command_kind)
                            parser.print_help()
                        case CommandKind.RULES:
                            logger.debug(
                                "   Executing %s command.", command_kind)
                            parser.print_rules()
                        case CommandKind.SAVE_AND_QUIT | CommandKind.SAVE_HISTORY:
                            logger.debug(
                                "   Executing %s command.", command_kind)
                            save_board_state_history(self.board)
                            logger.debug("   Game saved, exiting.")
                            sys.exit(0)
                        case CommandKind.FORFEIT:
                            logger.debug(
                                "   %s executed %s command.", self.current_player.name, command_kind)
                            print(f"{self.current_player.name} forfeited.")
                            self.switch_player()
                            logger.debug(
                                "   Game Over, %s wins! Exiting.", self.current_player.name)
                            print(
                                f"Game Over, {self.current_player.name} wins!")
                            sys.exit(0)
                        case CommandKind.RESTART:
                            logger.debug(
                                "   Executing %s command.", command_kind)
                            self.board.restart()
                            logger.debug("   Board restarted to initial state")
                        case CommandKind.QUIT:
                            logger.debug(
                                "   Executing %s command.", command_kind)
                            print("Exiting without saving...")
                            sys.exit(0)
                        case _:
                            logger.debug(
                                "   Invalid command: %s.", command_kind)
                            print("Invalid command. Try again.")
                            parser.print_help()

            except CommandParserException as e:
                log.log_error_message(
                    e, context=f"Failed to parse command: {command_str}")

                print(f"Error: {e}\nInvalid command. Please try again.")
                parser.print_help()


class BlitzGame(NormalGame):
    '''
    A class representing a Blitz game of Othello. A time limit has been
    added to the normal game rules.
    '''

    def __init__(self, filename: str, board_size: BoardSize = BoardSize.EIGHT_BY_EIGHT, time: int = None):
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
        logger.debug(
            "Entering initialization function for Blitz mode, from game_modes.py.")
        super().__init__(filename, BoardSize(board_size)
                         if isinstance(board_size, int) else board_size)
        self.blitz_timer = BlitzTimer(
            time if time is not None else DEFAULT_BLITZ_TIME)
        self.blitz_timer.start_timer('black')
        logger.debug(
            "   BlitzGame initialized, current player: ", self.current_player)

    def switch_player(self):
        """
        Switches the current player, updating the Blitz timer for the next player.

        If a player's time has expired, the game is over and the winner is printed.
        Otherwise, the Blitz timer is updated by switching the current player and
        starting the timer for the new player.
        """
        logger.debug(
            "Entering switch_player function for Blitz mode, from game_modes.py.")
        if self.blitz_timer.is_time_up('black'):
            logger.debug("   Black's time is up. White wins.")
            print("Black's time is up! White wins!")
            sys.exit(0)
        elif self.blitz_timer.is_time_up('white'):
            logger.debug("   White's time is up. Black wins.")
            print("White's time is up! Black wins!")
            sys.exit(0)

        super().switch_player()  # Switch player as normal
        next_player = 'white' if self.current_player == Color.WHITE else 'black'
        logger.debug("   Changing timer to player %s.", next_player)
        self.blitz_timer.change_player(next_player)

    def display_time(self):
        """
        Prints the remaining time for both players.

        This method prints the formatted string returned by BlitzTimer.display_time,
        which shows the remaining time for both black and white players in minutes and
        seconds.
        """
        logger.debug(
            "Entering display_time function for Blitz mode, from game_modes.py.")
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
        logger.debug(
            "Entering check_game_over function for Blitz mode,"
            " from game_modes.py, with parameter possible_moves.")
        if self.blitz_timer.is_time_up('black'):
            logger.debug("   Black's time is up. White wins.")
            print("Black's time is up! White wins!")
            sys.exit(0)
        elif self.blitz_timer.is_time_up('white'):
            logger.debug("   White's time is up. Black wins.")
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
        logger.debug(
            "Entering play function for Blitz mode, from game_modes.py.")
        parser = CommandParser(board_size=self.board.size.value)

        while True:
            self.display_board()
            possible_moves = self.get_possible_moves()
            if self.check_game_over(possible_moves):
                continue

            self.display_possible_moves(possible_moves)
            command_str = input("Enter your move or command: ").strip()
            logger.debug("   Player input: '%s'.", command_str)

            try:
                command_result = parser.parse_str(command_str)

                if command_result[0] == CommandKind.PLAY_MOVE:
                    kind = command_result[0]
                    play_command = command_result[1]
                    x_coord, y_coord = play_command.x_coord, play_command.y_coord
                    logger.debug(
                        "   Play move command at (%s, %s).", x_coord, y_coord)

                    if not self.process_move(x_coord, y_coord, possible_moves):
                        continue

                    self.switch_player()

                else:
                    kind = command_result[0]
                    match kind:
                        case CommandKind.HELP:
                            logger.debug(
                                "   Executing %s command.", command_result[0])
                            parser.print_help()
                        case CommandKind.RULES:
                            logger.debug(
                                "   Executing %s command.", command_result[0])
                            parser.print_rules()
                        case CommandKind.SAVE_AND_QUIT | CommandKind.SAVE_HISTORY:
                            logger.debug(
                                "   Executing %s command.", command_result[0])
                            save_board_state_history(self.board)
                            logger.debug("   Game saved, exiting.")
                            sys.exit(0)
                        case CommandKind.FORFEIT:
                            logger.debug(
                                "   %s executed %s command.", self.current_player.name, command_result[0])
                            print(f"{self.current_player.name} forfeited.")
                            self.switch_player()
                            logger.debug(
                                "   Game Over, %s wins! Exiting.", self.current_player.name)
                            print(
                                f"Game Over, {self.current_player.name} wins!")
                            sys.exit(0)
                        case CommandKind.RESTART:
                            logger.debug(
                                "   Executing %s command.", command_result[0])
                            self.board.restart()
                            logger.debug("   Board restarted to initial state")
                        case CommandKind.QUIT:
                            logger.debug(
                                "   Executing %s command. Exiting without saving.", command_result[0])
                            print("Exiting without saving...")
                            sys.exit(0)
                        case _:
                            logger.debug("   Invalid command: %s", command_str)
                            print("Invalid command. Try again.")
                            parser.print_help()

            except CommandParserException as e:
                log.log_error_message(
                    e, context=("Failed to parse command: %s.", command_str))
                print(f"Error: {e}")
                print("Invalid command. Please try again.")
                continue
            self.display_time()


class AIMode(NormalGame):
    '''
    A class representing a game mode where a player faces an AI opponent.
    '''

    def __init__(self, filename=None, board_size=BoardSize.EIGHT_BY_EIGHT, ai_color: Color = Color.BLACK, depth=3, algorithm="minimax", heuristic="coin_parity"):
        """
        Initialize the AI mode with a specified AI color, depth, algorithm, and heuristic.

        :param board_size: The size of the Othello board.
        :param ai_color: The color the AI will play as (Black or White).
        :param depth: The depth of the search tree for AI.
        :param algorithm: The search algorithm to use ("minimax" or "alphabeta").
        :param heuristic: The heuristic function to evaluate board states.
        """
        super().__init__(filename, board_size)

        if isinstance(ai_color, str):
            ai_color = ai_color.lower()
            if ai_color == 'black':
                self.ai_color = Color.BLACK
            elif ai_color == 'white':
                self.ai_color = Color.WHITE
            else:
                self.ai_color = ai_color
        elif not isinstance(ai_color, Color):
            raise ValueError(
                f"Invalid ai_color type: {type(ai_color)}. Must be a string or Color enum.")

        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic

    def get_ai_move(self, possible_moves):
        """
        Determines the AI's move using Minimax or Alpha-Beta Pruning.

        :param possible_moves: A bitboard of the possible capture moves for the AI.
        :return: A tuple (x, y) of the chosen move coordinates.
        """
        best_move = find_best_move(
            self.board, self.depth, self.ai_color, True, self.algorithm, self.heuristic)
        return best_move if best_move != (-1, -1) else None

    def display_ai_move(self, coords):
        """Convert (row, col) coordinates to chess notation."""
        col, row = coords
        col_letter = chr(ord('a') + col)
        print(f"\nMove Played: {col_letter}{row+1}\n")

    def play(self):
        """
        Main game loop for AI mode.

        This function implements the main game loop for AI mode, similar to that of Normal mode.
        However, AI mode pits an AI against the player.

        The loop consists of the following steps:

        1. Display the current state of the board.
        2. Calculate the possible moves for the current player.
        3. If the game is over, proceed to the next iteration.
        4. Display the possible moves.
        5. Obtain a move from the current player.
        6. If the move is invalid, proceed to the next iteration.
        7. Process the move by playing it on the board.
        8. Calculate the AI's move, based on a chosen algorithm.
        """
        logger.debug("Starting AI Mode game loop.")

        parser = CommandParser(board_size=self.board.size.value)

        while True:
            self.display_board()
            possible_moves = self.get_possible_moves()

            if self.check_game_over(possible_moves):
                continue

            self.display_possible_moves(possible_moves)
            if self.current_player == self.ai_color:
                print("AI is making a move...")
                ai_move = self.get_ai_move(possible_moves)
                if not self.process_move(ai_move[0], ai_move[1], possible_moves):
                    continue
                self.display_ai_move(ai_move)
                self.switch_player()
            else:
                command_str = input("Enter your move or command: ").strip()
                logger.debug(f"   Player input: '{command_str}'.")

                try:
                    command_result = parser.parse_str(command_str)
                    if command_result[0] == CommandKind.PLAY_MOVE:
                        kind = command_result[0]
                        play_command = command_result[1]
                        x_coord, y_coord = play_command.x_coord, play_command.y_coord
                        logger.debug(
                            f"   Play move command at ({x_coord}, {y_coord}).")

                        if not self.process_move(x_coord, y_coord, possible_moves):
                            continue

                        self.switch_player()

                    else:
                        kind = command_result[0]
                        match kind:
                            case CommandKind.HELP:
                                logger.debug(
                                    f"   Executing {command_result[0]} command.")
                                parser.print_help()
                            case CommandKind.RULES:
                                logger.debug(
                                    f"   Executing {command_result[0]} command.")
                                parser.print_rules()
                            case CommandKind.SAVE_AND_QUIT | CommandKind.SAVE_HISTORY:
                                logger.debug(
                                    f"   Executing {command_result[0]} command.")
                                save_board_state_history(self.board)
                                logger.debug("   Game saved, exiting.")
                                sys.exit(0)
                            case CommandKind.FORFEIT:
                                logger.debug(
                                    f"   {self.current_player.name} executed {command_result[0]} command.")
                                print(f"{self.current_player.name} forfeited.")
                                self.switch_player()
                                logger.debug(
                                    f"   Game Over, {self.current_player.name} wins! Exiting.")
                                print(
                                    f"Game Over, {self.current_player.name} wins!")
                                sys.exit(0)
                            case CommandKind.RESTART:
                                logger.debug(
                                    f"   Executing {command_result[0]} command.")
                                self.board.restart()
                                logger.debug(
                                    "   Board restarted to initial state")
                            case CommandKind.QUIT:
                                logger.debug(
                                    f"   Executing {command_result[0]} command. Exiting without saving.")
                                print("Exiting without saving...")
                                sys.exit(0)
                            case _:
                                logger.debug(
                                    f"   Invalid command: {command_str}.")
                                print("Invalid command. Try again.")
                                parser.print_help()

                except CommandParserException as e:
                    # log.log_error_message(
                    #    e, context=f"Failed to parse command: {command_str}.")

                    print("Invalid command. Please try again.")
                    continue
