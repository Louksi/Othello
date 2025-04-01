"""
Entry point for the othello executable.
"""

import logging

from othello.board_parser import BoardParser
import othello.parser as parser
import othello.logger as log
from othello.gui import OthelloGUI
from othello.cli import OthelloCLI
from othello.othello_board import BoardSize, OthelloBoard
from othello.controllers import (
    AIPlayer,
    GameController,
    HumanPlayer,
    RandomPlayer,
)
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

    display_config(config)

    controller = None
    size = BoardSize.from_value(config["size"])

    board = None

    # first we try to retrieve a save from given filename if it exists
    filename = config["filename"]
    if filename is None:
        board = OthelloBoard(size)
    else:
        try:
            with open(filename, "r") as file:
                file_content = file.read()
            board = BoardParser(file_content).parse()
        except FileNotFoundError:
            context = "File not found: %s" % filename
            log.log_error_message(FileNotFoundError, context=context)
            raise
        except Exception as err:
            log.log_error_message(err, context="Failed to load game.")
            raise

    # then we setup black and white, specifying if they are AI players or not
    black_player = (
        AIPlayer(board, config["ai_depth"], config["ai_mode"], config["ai_heuristic"])
        if mode == parser.GameMode.AI.value and config["ai_color"] == "X"
        else HumanPlayer()
    )
    white_player = (
        AIPlayer(board, config["ai_depth"], config["ai_mode"], config["ai_heuristic"])
        if mode == parser.GameMode.AI.value and config["ai_color"] == "O"
        else HumanPlayer()
    )
    logger.debug(f"   Black player is of class {black_player.__class__}.")
    logger.debug(f"   White player is of class {white_player.__class__}.")

    # then we setup the game controller depenging of the gamemode given
    if mode == parser.GameMode.BLITZ.value:
        controller = GameController(
            board, black_player, white_player, True, config["blitz_time"]
        )
    elif mode == parser.GameMode.CONTEST.value:
        log.log_error_message(
            "#todo#", context="The contest mode is not implemented yet."
        )
        raise Exception("//todo")
    else:
        controller = GameController(board, black_player, white_player)

    # finally, we run either in gui or in cli
    if config["gui"]:
        logger.debug("Starting graphical user interface.")
        gui = OthelloGUI(controller)
        gui.run()
    else:
        logger.debug("Starting command line user interface.")
        cli = OthelloCLI(controller, controller.is_blitz())
        cli.play()


if __name__ == "__main__":
    main()
