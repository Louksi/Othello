"""
Entry point for the othello executable.
"""

import sys
import logging

from othello.board_parser import BoardParser
import othello.parser as parser
import othello.logger as log
from othello.gui import OthelloGUI
from othello.cli import OthelloCLI
from othello.othello_board import BoardSize, OthelloBoard
from othello.controllers import GameController, AIPlayerGameController
from othello.config import display_config


def main():
    """
    Entry point for the Othello game.

    The main function is responsible for handling the game loop based on the
    provided command line arguments. It will parse the arguments, set up the
    game mode, and start the game loop.

    The game loop will print the current state of the board, the current player,
    and the valid moves for that player. It will then ask the player for input,
    and attempt to make the move. If the move is invalid, it will ask again.
    If the move is valid, it will update the board and switch to the other player.

    The game loop will continue until the game is over, or the user quits.

    Args:
        None

    Returns:
        None
    """
    mode, config = parser.parse_args()

    log.logging_config(config["debug"])
    logger = logging.getLogger("Othello")

    logger.debug("Start of a Othello game.")
    logger.debug("Debug mode is enabled.")
    logger.debug("Game mode: %s", mode)

    current_config = parser.default_config.copy()
    current_config.update(config)

    # filename_prefix = "config"

    # configuration.save_config(current_config, config["filename"])

    # loaded_config = configuration.load_config(config["filename"])
    # print("Config loaded:", config)

    display_config(config)

    controller = None
    size = BoardSize.from_value(config["size"])

    board = None
    filename = config["filename"]
    if filename is None:
        board = OthelloBoard(size)
    else:
        try:
            with open(filename, "r") as file:
                file_content = file.read()
            board = BoardParser(file_content).parse()
        except FileNotFoundError:
            logger.error("File not found: %s", filename)
            raise
        except Exception as err:
            logger.error("Failed to load game: %s", err)
            raise

    match mode:
        case parser.GameMode.NORMAL.value:
            controller = GameController(board)
        case parser.GameMode.BLITZ.value:
            controller = GameController(board, True, config["blitz_time"])
        case parser.GameMode.CONTEST.value:
            logger.error("Contest mode is not implemented yet.")
            print("//todo")
            sys.exit(1)
        case parser.GameMode.AI.value:
            controller = AIPlayerGameController(
                OthelloBoard(size),
                config["ai_color"],
                config["ai_depth"],
                config["ai_mode"],
                config["ai_heuristic"],
            )

        case _:
            logger.error("Invalid game mode: %s", mode)
            print("Unknown game mode. Exiting.")
            sys.exit(1)
    if config["gui"]:
        logger.debug("Starting graphical user interface.")
        gui = OthelloGUI(controller)
        gui.run()
    else:
        logger.debug("Starting command-line interface.")
        OthelloCLI(controller, controller.is_blitz, config["blitz_time"]).play()


if __name__ == "__main__":
    main()
