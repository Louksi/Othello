"""
A class to help parsing cli user input
"""
from dataclasses import dataclass
from enum import Enum, auto
import re
import argparse
from typing import Tuple, Union


class CommandParserException(Exception):
    """
    Thrown on bad input string
    """

    def __init__(self, bad_str: str) -> None:
        super().__init__(f"unrecognized string {bad_str}")


class CommandKind(Enum):
    """
    Kind of commands that are available. Pretty self-explainatory
    """
    HELP = auto()
    RULES = auto()
    SAVE_AND_QUIT = auto()
    SAVE_HISTORY = auto()
    FORFEIT = auto()
    RESTART = auto()
    PLAY_MOVE = auto()
    QUIT = auto()


@dataclass
class PlayCommand:
    """
    An actual othello play with its coords
    """
    x_coord: int
    y_coord: int


CommandType = Union[  # This type is used to kind of mimic some sort of algebraic datatype
    Tuple[CommandKind.PLAY_MOVE, PlayCommand],
    Tuple[Union[
        CommandKind.HELP,
        CommandKind.RULES,
        CommandKind.SAVE_AND_QUIT,
        CommandKind.SAVE_HISTORY,
        CommandKind.FORFEIT,
        CommandKind.RESTART,
        CommandKind.QUIT]]
]


class CommandParser:
    """
    A class that helps parsing cli user commands.
    """

    def __init__(self, board_size: int):
        # Fix to include the last column
        str_board_max_column = chr(ord('a') + board_size - 1)
        str_board_max_line = board_size
        column_rx = rf"[a-{str_board_max_column}]"
        line_rx = rf"[1-{str_board_max_line}]"
        command_regex_str = rf"(\?|{column_rx}{line_rx}|restart|r|sh|s|ff|q)"
        move_regex_str = rf"(({column_rx})({line_rx}))"
        self.command_regex = re.compile(command_regex_str)
        self.move_regex = re.compile(move_regex_str)

        # Set up argparse for help display
        self.help_parser = argparse.ArgumentParser(
            description='Othello Game Commands',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False  # Don't add the default help
        )

        # Add command descriptions
        self.help_parser.add_argument(
            '?', action='store_true', help='Show this help message')
        self.help_parser.add_argument(
            'r', action='store_true', help='Show the game rules')
        self.help_parser.add_argument(
            's', action='store_true', help='Save game and quit')
        self.help_parser.add_argument(
            'sh', action='store_true', help='Save game history')
        self.help_parser.add_argument(
            'ff', action='store_true', help='Forfeit the current game')
        self.help_parser.add_argument(
            'restart', action='store_true', help='Restart the game')
        self.help_parser.add_argument(
            'q', action='store_true', help='Quit without saving')
        self.help_parser.add_argument(
            'move',
            metavar=f'[a-{str_board_max_column}][1-{str_board_max_line}]',
            nargs='?',
            help=f'Play a move (e.g., a1, {str_board_max_column}{str_board_max_line})'
        )

    def print_help(self):
        """
        Display help information using argparse.
        """
        print("\nOthello Game Help")
        print("=================")
        self.help_parser.print_help()
        print("\nExample commands:")
        print("  a1     - Play at position a1")
        print("  ?      - Show this help message")
        print("  r      - Show the game rules")
        print("  q      - Quit without saving")
        print("  s      - Save and quit")
        print("  sh     - Save game history")
        print("  ff     - Forfeit the current game")
        print("  restart - Restart the game")
        print("\nCoordinate format: [column][row] (e.g., a1, b2)")

    def print_rules(self):
        """
        Display the rules of Othello/Reversi
        """
        print("\nOthello/Reversi Rules")
        print("====================")
        print("Objective:")
        print("  The goal is to have the majority of your color discs on the board when the game ends.")
        print("\nSetup:")
        print("  - The game is played on an 8×8 board (though our implementation may vary)")
        print("  - The game begins with four discs placed in the center in a 2×2 pattern,")
        print("    with same-colored discs positioned diagonally.")
        print("  - Black moves first")
        print("\nGameplay:")
        print("  1. A move consists of placing a disc of your color on an empty square")
        print("  2. For a move to be valid, it must 'outflank' at least one of your opponent's discs")
        print("  3. To outflank means to place a disc such that one or more of your opponent's discs")
        print("     are bordered at each end by a disc of your color (in a straight line)")
        print(
            "  4. All of the opponent's discs that are outflanked are flipped to your color")
        print("  5. If a player cannot make a valid move, their turn is skipped")
        print("  6. The game ends when neither player can make a valid move")
        print("\nWinning:")
        print(
            "  The player with the most discs of their color on the board at the end wins.")
        print("  If both players have the same number of discs, the game is a draw.")
        print("\nPress Enter to continue playing...")
        input()

    def parse_str(self, command_str: str) -> CommandType:
        """
        Returns a constructed CommandType for a supplied string, if the string is valid
        Else raises an exception

        :param command_str: The string to be parsed
        :param type: str
        :returns: A constructed command tuple
        :raises CommandParserException: if the string is invalid
        """
        matches = self.command_regex.fullmatch(command_str)

        if matches is None:
            raise CommandParserException(command_str)
        match_result = matches.group(1)
        if match_result == "?":
            return (CommandKind.HELP,)
        elif match_result == "r":
            return (CommandKind.RULES,)
        elif match_result == "s":
            return (CommandKind.SAVE_AND_QUIT,)
        elif match_result == "sh":
            return (CommandKind.SAVE_HISTORY,)
        elif match_result == "ff":
            return (CommandKind.FORFEIT,)
        elif match_result == "restart":
            return (CommandKind.RESTART,)
        elif match_result == "q":
            return (CommandKind.QUIT,)
        else:
            play_matches = self.move_regex.match(match_result)
            col_raw = play_matches.group(2)
            line_raw = play_matches.group(3)
            if col_raw is None or line_raw is None:
                raise CommandParserException(command_str)
            move_x_coord = ord(col_raw) - ord('a')
            move_y_coord = int(line_raw)-1
            play_command = PlayCommand(move_x_coord, move_y_coord)
            return (CommandKind.PLAY_MOVE, play_command)
