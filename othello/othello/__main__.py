'''
Entry point for the othello executable.
'''

import sys
import logging

import othello.parser as parser
import othello.game_modes as Modes
import othello.logger as log
from othello.gui import OthelloGUI
from othello.othello_board import BoardSize, OthelloBoard
from othello.controllers import GameController


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
    print("Config loaded:", config)

    match mode:
        case parser.GameMode.NORMAL.value:
            print("Starting Normal Mode...")
            if config["gui"]:
                size = BoardSize.from_value(config["size"])
                board = GameController(OthelloBoard(size))
                gui = OthelloGUI(board)
                gui.run()
            else:
                Modes.NormalGame(config["filename"], config["size"]).play()

        case parser.GameMode.BLITZ.value:
            print("Starting Blitz Mode...")
            print(
                f"Blitz mode with time limit: {config['blitz_time']} minutes")
            if config["gui"]:
                size = BoardSize.from_value(config["size"])
                board = GameController(OthelloBoard(size))
                gui = OthelloGUI(board)
                gui.run()
            else:
                Modes.BlitzGame(config["filename"],
                                config["size"], config["blitz_time"]).play()

        case parser.GameMode.CONTEST.value:
            print("Starting Contest Mode...")
            print(f"Loading contest from file: {config['cFile']}")

        case parser.GameMode.AI.value:
            print("Starting AI Mode...")
            if config["gui"]:
                size = BoardSize.from_value(config["size"])
                board = OthelloBoard(size)
                # Create a GUI with AI capabilities
                gui = OthelloGUI(board)
                gui.run()
            else:
                Modes.AIMode(config["filename"], config["size"], "black", config["ai_depth"],
                             config["ai_mode"], config["ai_heuristic"]).play()
        case _:
            print("Unknown game mode. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()
