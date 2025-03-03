'''
Entry point for the othello executable.
'''
import sys
from othello.gui import OthelloGUI
from othello.othello_board import BoardSize, OthelloBoard
import othello.parser as parser
import othello.game_modes as Modes
import othello.config as configuration


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
    mode, config = parse_args()

    current_config = default_config.copy()
    current_config.update(config)

    filename_prefix = "config"

    configuration.save_config(current_config, filename_prefix)

    loaded_config = configuration.load_config(filename_prefix)
    print("Config loaded:", loaded_config)
    b = OthelloBoard(BoardSize.SIX_BY_SIX)
    g = OthelloGUI(b)
    g.run()
    exit()

    match mode:
        case GameMode.NORMAL.value:
            print("Starting Normal Mode...")
            Modes.NormalGame(config["size"]).play()

        case GameMode.BLITZ.value:
            print("Starting Blitz Mode...")
            Modes.BlitzGame(config["size"], config["blitz_time"]).play()
            print(f"Blitz mode with time limit: {config['bTime']} minutes")

        case GameMode.CONTEST.value:
            print("Starting Contest Mode...")
            print(f"Loading contest from file: {config['cFile']}")

        case GameMode.AI.value:
            print("Starting AI Mode...")
            print(f"AI plays as: {config['AIColor']}")

        case _:
            print("Unknown game mode. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()
