import argparse
import sys
from typing import Optional, Tuple
from enum import Enum


# VARIABLES

class GameMode(Enum):
    NORMAL = "normal"
    BLITZ = "blitz"
    CONTEST = "contest"
    AI = "ai"


class aiColor(Enum):
    BLACK = "X"
    WHITE = "O"
    ALL = "A"


VALID_SIZES = [6, 8, 10, 12]
VERSION = "0.1.0"
DEFAULT_BLITZ_TIME = 30
VALID_AICOLORS = [x.value for x in aiColor]


# PARSER

def createParser() -> argparse.ArgumentParser:
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
    # while help is included by default in argparse, we'll add it here explicitly for documentation purposes
    # whoops, adding it creates a conflict, guess we won't add it then
    # parser.add_argument( "-h", "--help",
    #         action = "help",
    #         help = "Display this help message and exit"
    #         )

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

    return parser


# PARSING

def parse_args() -> Tuple[GameMode, dict]:
    """
    Parse the arguments and checks for errors.

    Returns:
      Tuple[GameMode, dict]: Game mode and dictionary containing the configuration

    Raises:
      SystemExit: if invalid arguments are provided
    """

    parser = createParser()
    args, unknown_args = parser.parse_known_args()

    # invalid option raises an error
    if unknown_args:
        parse_error(parser, f"Invalid option(s): {', '.join(unknown_args)}")

    # specifying more than one game mode raises an error
    if (args.contest and args.blitz) or (args.contest and args.ai) or (args.ai and args.blitz):
        parse_error(
            parser, f"Specifying more than one game mode is not possible")

    # game mode
    mode = GameMode.NORMAL
    if args.contest:
        mode = GameMode.CONTEST
    elif args.blitz:
        mode = GameMode.BLITZ
    elif args.ai:
        mode = GameMode.AI

    # starting a game from a file and changing specific options raises an error
    illegalOptionsWithFile = ["size", "blitz", "contest", "ai"]

    if args.filename and not (args.size or args.blitz or args.contest or args.ai):
        parse_error(
            parser, f"Cannot specify options that break the game configuration when loading a game from a file")

    # setting time if GM is not blitz raises an error
    if args.time and not args.blitz:
        parse_error(
            parser, "Time option is only valid in blitz mode: -b or --blitz")

    # setting negative time limit raises an error
    if args.time and args.time <= 0:
        parse_error(parser, "Time limit must be positive")

    # not specifying a file in contest mode raises an error
    if mode == GameMode.CONTEST and not args.contest:
        parse_error(parser, "Contest mode requires a file (-c FILENAME)")

    if args.contest is not None and args.contest == "":
        parse_error(parser, "Contest mode requires a valid filename")

    # specifying an invalid color for the ai player raises an error
    if args.ai and (args.ai not in VALID_AICOLORS):
        parse_error(parser, f"Invalid AI color: {args.ai}")

    # build configuration dictionary
    config = {
        # "mode": mode,
        "filename": args.filename,
        "size": args.size,
        "debug": args.debug,
        # "blitz": args.blitz,
        # "bTime": args.time or DEFAULT_BLITZ_TIME,
        "contest": args.contest,
        "cFile": args.filename,
        # "ai": args.ai,
        # "aiColor": args.ai,
    }

    # specify game mode
    if mode == GameMode.BLITZ:
        config["blitz"] = args.blitz
        config["bTime"] = args.time or DEFAULT_BLITZ_TIME
    elif mode == GameMode.CONTEST:
        config["contest"] = args.contest
        config["cFile"] = args.contest
    elif mode == GameMode.AI:
        config["ai"] = args.ai
        config["aiColor"] = args.ai

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
