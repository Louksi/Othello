"""Game Modes for Othello"""

import logging
import sys

import othello.parser as parser
import othello.logger as log
from othello.command_parser import CommandParser, CommandKind, CommandParserException
from othello.board_parser import BoardParser
from othello.parser import DEFAULT_BLITZ_TIME
from othello.config import save_board_state_history
from othello.othello_board import BoardSize, GameOverException, OthelloBoard, Color
from othello.blitz_timer import BlitzTimer
from othello.controllers import (
    GameController,
)


logger = logging.getLogger("Othello")


class OthelloCLI:
    """
    A class representing a Normal Othello game.
    """

    NB_PLAYS_IN_HISTORY = 5

    def __init__(
        self,
        controller: GameController,
        blitz_mode: bool = False,
        blitz_time: int | None = None,
    ):
        # Initialize the base board first
        self.board = controller
        self.blitz_mode = blitz_mode
        if blitz_mode:
            self.blitz_timer = BlitzTimer(
                blitz_time if blitz_time is not None else DEFAULT_BLITZ_TIME
            )
            self.blitz_timer.start_timer("black")

        logger.debug(
            "cli initialized, current_player: %s.", self.board.get_current_player()
        )

    def display_board(self):
        """
        Display the current state of the board and indicate the current player's turn.

        This function prints a string representation of the Othello board and
        indicates which player's turn it is by displaying the player's name
        and corresponding symbol.
        """
        logger.debug("Entering display_board function from cli.py.")
        print(str(self.board))
        print(
            f"\n{self.board.get_current_player().name}'s turn ({self.board.get_current_player().value})"
        )

    def check_game_over(self, possible_moves):
        """
        Checks if the game is over by delegating to the board's is_game_over method.
        If the game is over, prints the appropriate game over message and final score.

        :param possible_moves: A bitboard of the possible capture moves for the current player.
        :type possible_moves: Bitboard
        :return: True if the game is over, False otherwise.
        :rtype: bool
        """
        logger.debug("Entering check_game_over function from game_modes.py.")

        if self.blitz_mode:
            if self.blitz_timer.is_time_up("black"):
                print("Black's time is up! White wins!")
                return True
            elif self.blitz_timer.is_time_up("white"):
                print("White's time is up! Black wins!")
                return True

        if self.board.is_game_over():
            logger.debug("Game over condition detected.")

            # Print final score
            black_score = self.board.popcount(Color.BLACK)
            white_score = self.board.popcount(Color.WHITE)
            logger.debug("Final score - Black: %s, White: %s", black_score, white_score)
            print(f"Final score - Black: {black_score}, White: {white_score}")

            # Determine winner
            if black_score > white_score:
                logger.debug("Black wins.")
                print("Black wins!")
            elif white_score > black_score:
                logger.debug("White wins.")
                print("White wins!")
            else:
                logger.debug("The game is a tie.")
                print("The game is a tie!")

            return True

        # If no moves for current player but game isn't over (other player can still move)
        if possible_moves.bits == 0:
            logger.debug(
                "No moves available for %s player. Skipping turn.",
                self.board.get_current_player(),
            )
            print(
                f"No valid moves for {self.board.get_current_player().name}. Skipping turn."
            )

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
            " with parameter possible_moves."
        )
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

        x_coord = ord(move[0]) - ord("a")
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
            "%s, y_coord: %s, and possible_moves.",
            x_coord,
            y_coord,
        )
        if not possible_moves.get(x_coord, y_coord):
            logger.debug("   The move is not legal to play")
            print("Invalid move. Not a legal play. Try again.")
            return False
        logger.debug("   Move (%s, %s) is legal, playing.", x_coord, y_coord)
        if self.blitz_mode:
            current = (
                "black" if self.board.get_current_player() == Color.BLACK else "white"
            )
            self.blitz_timer.change_player("white" if current == "black" else "black")

        try:
            self.board.play(x_coord, y_coord)
        except GameOverException:
            print("game over")
        return True

    def check_parser_input(self, command_str, command_kind, *args):
        """
        Checks if the given command from the parser is valid and executes it.

        If the command is invalid, it prints an error message and prompts the
        player again. If the command is valid, it processes the move and switches
        the player. If the player has won, it prints a message and exits.

        :param command_str: The command string from the parser.
        :param command_kind: The type of command.
        :param args: Additional arguments from the parser.
        :type command_str: str
        :type command_kind: CommandKind
        :type args: tuple
        :return: True if the command is valid, False if the command is invalid.
        :rtype: bool
        """
        if command_kind == CommandKind.PLAY_MOVE:
            play_command = args[0]
            x_coord, y_coord = play_command.x_coord, play_command.y_coord
            logger.debug("   Play move command at (%s, %s).", x_coord, y_coord)

            if not self.process_move(
                x_coord,
                y_coord,
                self.board.get_possible_moves(self.board.get_current_player()),
            ):
                print("Invalid move. Try again.")
                return

        else:
            match command_kind:
                case CommandKind.HELP:
                    logger.debug("   Executing %s command.", command_kind)
                    self.parser.print_help()
                case CommandKind.RULES:
                    logger.debug("   Executing %s command.", command_kind)
                    self.parser.print_rules()
                case CommandKind.SAVE_AND_QUIT | CommandKind.SAVE_HISTORY:
                    logger.debug("   Executing %s command.", command_kind)
                    save_board_state_history(self.board)
                    logger.debug("   Game saved, exiting.")
                    sys.exit(0)
                case CommandKind.FORFEIT:
                    logger.debug(
                        "   %s executed %s command.",
                        self.board.get_current_player().name,
                        command_kind,
                    )
                    print(f"{self.board.get_current_player().name} forfeited.")
                    self.board.current_player = ~self.board.get_current_player()
                    logger.debug(
                        "   Game Over, %s wins! Exiting.",
                        self.board.current_player.name,
                    )
                    print(f"Game Over, {self.board.current_player.name} wins!")
                    sys.exit(0)
                case CommandKind.RESTART:
                    logger.debug("   Executing %s command.", command_kind)
                    self.board.restart()
                    logger.debug("   Board restarted to initial state")
                case CommandKind.QUIT:
                    logger.debug("   Executing %s command.", command_kind)
                    print("Exiting without saving...")
                    sys.exit(0)
                case _:
                    logger.debug("   Invalid command: %s.", command_kind)
                    print("Invalid command. Try again.")
                    self.parser.print_help()

    def display_history(self):
        """
        Displays the last self.NB_PLAYS_IN_HISTORY turns
        """
        to_print = "Play history:\n" + "\n".join(
            [
                f"{play[4]} placed a piece at {chr(ord('A') + play[2])}{play[3] + 1}"
                for play in self.board.get_history()[-self.NB_PLAYS_IN_HISTORY :]
            ]
        )
        print(to_print, "\n")

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
        self.parser = CommandParser(board_size=self.board.size.value)

        possible_moves = self.board.get_possible_moves(self.board.get_current_player())

        def human_play_callback():
            if self.blitz_mode:
                print(self.blitz_timer.display_time())
            command_str = input("Enter your move or command: ").strip()
            logger.debug("   Player input: '%s'.", command_str)
            try:
                command_kind, *args = self.parser.parse_str(command_str)
                self.check_parser_input(command_str, command_kind, *args)

            except CommandParserException as e:
                log.log_error_message(
                    e, context=f"Failed to parse command: {command_str}"
                )

                print(f"Error: {e}\nInvalid command. Please try again.")
                self.parser.print_help()

        def turn_display():
            print(f"=== turn {self.board.get_turn_number()} ===")
            self.display_history()
            self.display_board()
            possible_moves = self.board.get_possible_moves(
                self.board.get_current_player()
            )
            self.display_possible_moves(possible_moves)

        self.board.human_play_callback = human_play_callback
        self.board.post_play_callback = turn_display
        turn_display()

        while True:
            if self.check_game_over(possible_moves):
                break

            self.board.next_move()
