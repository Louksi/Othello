"""
A class to help parsing cli user input
"""
from dataclasses import dataclass
from enum import Enum, auto
import re
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
        CommandKind.RESTART]]
]


class CommandParser:
    """
    A class that helps parsing cli user commands.
    """

    def __init__(self, board_size: int):
        str_board_max_column = chr(ord('a') + board_size)
        str_board_max_line = board_size
        column_rx = rf"[a-{str_board_max_column}]"
        line_rx = rf"[1-{str_board_max_line}]"
        command_regex_str = rf"(\?|{column_rx}{line_rx}|restart|r|sh|s|ff)"
        move_regex_str = rf"(({column_rx})({line_rx}))"
        self.command_regex = re.compile(command_regex_str)
        self.move_regex = re.compile(move_regex_str)

    def parse_str(self, command_str: str) -> CommandType:
        """
        Returns a constructed CommandType for a supplied string, if the string is valid
        Else raises an exception

        :param command_str: The string to be parsed
        :param type: str
        :returns: A constructed command tuple
        :raises CommandParserException: if the string is invalid
        """
        matches = self.command_regex.match(command_str)
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
