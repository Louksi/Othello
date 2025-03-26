"""
Program arguments parsing
"""

import sys
from typing import Tuple
from enum import Enum
from typing import Any
import argparse

import othello
from othello.othello_board import Color

# VARIABLES


class GameMode(Enum):
    """
    Enum matching gamemode options to its string representation
    """
    NORMAL = "normal"
    BLITZ = "blitz"
    CONTEST = "contest"
    AI = "ai"


class AIColor(Enum):
    """Enum matching ai color option to its string representation"""
    BLACK = "X"
    WHITE = "O"
    ALL = "A"


class AIMode(Enum):
    """Enum matching ai algorithm mode option to its string representation"""
    MINIMAX = "minimax"
    ALPHABETA = "ab"


class AIHeuristic(Enum):
    """Enum matching ai heuristic option to its string representation"""
    DEFAULT = "default"
    OTHER = "other"


VALID_SIZES = [6, 8, 10, 12]
VERSION = othello.__version__
DEFAULT_BLITZ_TIME = 30
VALID_AICOLORS = [x.value for x in AIColor]
VALID_AIMODES = [x.value for x in AIMode]
VALID_AIHEURISTICS = [x.value for x in AIHeuristic]
DEFAULT_AI_DEPTH = 3
DEFAULT_AI_TIME = 5
DEFAULT_AI_HEURISTIC = "default"
DEFAULT_GUI = False

# Default configuration
default_config = {
    "mode": GameMode.NORMAL.value,
    "filename": None,
    "size": 8,
    "debug": False,
    "blitz_time": DEFAULT_BLITZ_TIME,
    "ai_color": AIColor.BLACK.value,
    "ai_mode": "minimax",
    "ai_shallow": False,
    "ai_depth": 3,
    "ai_heuristic": "default",
    "ai_time": 5,
    "gui": DEFAULT_GUI
}


# PARSER

def create_parser() -> argparse.ArgumentParser:
    """
    Initialize and configure the argument parser.
    """

    # parser
    parser = argparse.ArgumentParser(
        prog="othello",
        description="Othello - Reversi game implementation",
        usage="othello [OPTIONS] [FILENAME]"
    )

    # file
    parser.add_argument("filename",
                        nargs="?",
                        help="Load game from specified file"
                        )

    # options
    parser.add_argument("-V", "--version",
                        action="version",
                        version=f"%(prog)s {VERSION}",
                        help="Display the program's current version and exit"
                        )

    parser.add_argument("-d", "--debug",
                        action="store_true",
                        help="Enable debug mode, will display debug information during the game"
                        )

    parser.add_argument("-s", "--size",
                        type=int,
                        choices=VALID_SIZES,
                        default=8,
                        metavar="SIZE",
                        help=f"Set board size to one of {VALID_SIZES}, default is {VALID_SIZES[1]}"
                        )

    parser.add_argument("-b", "--blitz",
                        action="store_true",
                        help=f"Enable blitz game mode, (default time for each player: {DEFAULT_BLITZ_TIME} minutes)"
                        )

    parser.add_argument("-t", "--time",
                        type=int,
                        metavar="TIME",
                        help=f"Set initial time (in minutes) for each player in Blitz mode, default is {DEFAULT_BLITZ_TIME} minutes"
                        )

    parser.add_argument("-c", "--contest",
                        type=str,
                        metavar="FILENAME",
                        help="Enable contest game mode with specified file"
                        )

    parser.add_argument("-a", "--ai",
                        nargs="?",
                        const=VALID_AICOLORS[0],
                        choices=VALID_AICOLORS,
                        metavar="COLOR",
                        help="Enable AI game mode with optional color specification: black: 'X' / white: 'O' / all: 'A', default is black"
                        )

    parser.add_argument("--ai-mode",
                        type=str,
                        choices=VALID_AIMODES,
                        default=VALID_AIMODES[0],
                        help="Set AI algorithm mode: minimax: 'minimax' / alpha-beta: 'ab', default is minimax"
                        )

    parser.add_argument("--ai-shallow",
                        action="store_true",
                        help="Enable shallow AI mode, allows for a preliminary shallow exploration of the move tree"
                        )

    parser.add_argument("--ai-depth",
                        type=int,
                        default=DEFAULT_AI_DEPTH,
                        metavar="DEPTH",
                        help=f"Set AI search depth (root_depth = 0), default is {DEFAULT_AI_DEPTH}"
                        )

    parser.add_argument("--ai-heuristic",
                        type=str,
                        choices=VALID_AIHEURISTICS,
                        default=DEFAULT_AI_HEURISTIC,
                        metavar="HEURISTIC",
                        help=f"Set AI heuristic: default: 'default' / other: 'other', default is '{DEFAULT_AI_HEURISTIC}'"
                        )

    parser.add_argument("--ai-time",
                        type=int,
                        default=DEFAULT_AI_TIME,
                        metavar="TIME",
                        help=f"Set AI time limit (in seconds), default is {DEFAULT_AI_TIME} seconds"
                        )

    parser.add_argument("--gui",
                        action="store_true",
                        default=DEFAULT_GUI,
                        help="Launch the GUI version instead of the CLI one.")

    return parser


# PARSING

def parse_args() -> tuple[str, dict[str, Any]]:
    """
    Parse the arguments and checks for errors.

    Returns:
      Tuple[GameMode, dict]: Game mode and dictionary containing the configuration

    Raises:
      SystemExit: if invalid arguments are provided
    """

    parser = create_parser()
    args, unknown_args = parser.parse_known_args()

    # invalid option raises an error
    if unknown_args:
        parse_error(parser, f"Invalid option(s): {', '.join(unknown_args)}")

    # specifying more than one game mode raises an error
    if (args.contest and args.blitz) or (args.contest and args.ai) or (args.ai and args.blitz):
        parse_error(
            parser, "Specifying more than one game mode is not possible")

    # game mode
    mode = GameMode.NORMAL.value
    if args.contest:
        mode = GameMode.CONTEST.value
    elif args.blitz:
        mode = GameMode.BLITZ.value
    elif args.ai:
        mode = GameMode.AI.value

    # starting a game from a file and changing specific options raises an error
    # illegal_options_with_file = ["size", "blitz", "contest", "ai"]

    if args.filename and not (args.size or args.blitz or args.contest or args.ai):
        parse_error(
            parser, "Cannot specify options that break the game configuration when loading a game from a file")

    # setting time if GM is not blitz raises an error
    if args.time and not args.blitz:
        parse_error(
            parser, "Time option is only valid in blitz mode: -b or --blitz")

    # setting negative time limit raises an error
    if args.time and args.time <= 0:
        parse_error(parser, "Time limit must be positive")

    # not specifying a file in contest mode raises an error
    if mode == GameMode.CONTEST.value and args.contest is None:
        parse_error(parser, "Contest mode requires a file (-c FILENAME)")

    if args.contest is not None and args.contest == "":
        parse_error(parser, "Contest mode requires a valid filename")

    # specifying an invalid color for the ai player raises an error
    if args.ai and (args.ai not in VALID_AICOLORS):
        parse_error(parser, f"Invalid AI color: {args.ai}")

    # specifying a negative ai depth raises an error
    if args.ai_depth <= 0:
        parse_error(parser, "AI depth must be positive")

    # specifying a negative ai time limit raises an error
    if args.ai_time <= 0:
        parse_error(parser, "AI time limit must be positive")

    # build configuration dictionary
    config = {
        "mode": mode,
        "filename": args.filename,
        "size": args.size,
        "debug": args.debug,
        "blitz_time": DEFAULT_BLITZ_TIME,
        "ai_color": VALID_AICOLORS[0],
        "ai_mode": VALID_AIMODES[0],
        "ai_shallow": False,
        "ai_depth": DEFAULT_AI_DEPTH,
        "ai_heuristic": DEFAULT_AI_HEURISTIC,
        "ai_time": DEFAULT_AI_TIME,
        "gui": args.gui
    }

    # specify game mode
    if mode == GameMode.BLITZ.value:
        config["blitz_time"] = args.time or DEFAULT_BLITZ_TIME
    elif mode == GameMode.CONTEST.value:
        config["filename"] = args.contest
    elif mode == GameMode.AI.value:
        config["ai_color"] = args.ai or VALID_AICOLORS[0]
        config["ai_mode"] = args.ai_mode or VALID_AIMODES[0]
        config["ai_shallow"] = args.ai_shallow or False
        config["ai_depth"] = args.ai_depth or DEFAULT_AI_DEPTH
        config["ai_heuristic"] = args.ai_heuristic or DEFAULT_AI_HEURISTIC
        config["ai_time"] = args.ai_time or DEFAULT_AI_TIME

    return mode, config


# ERRORS

def parse_error(parser: argparse.ArgumentParser, message: str) -> None:
    """
    Display error message and help, then exit.

    Arguments:
      parser: the argument parser
      message: the error message to display
    """

    sys.stderr.write(f"Error parsing: {message}\n\n")
    parser.print_help(sys.stderr)
    sys.exit(1)
