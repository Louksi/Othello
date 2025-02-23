import sys
import othello.parser as parser
import othello.game_modes as Modes


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

    match mode:
        case parser.GameMode.NORMAL.value:
            print("Starting Normal Mode...")
            Modes.NormalGame(config["size"]).play()

        case parser.GameMode.BLITZ.value:
            print("Starting Blitz Mode...")
            Modes.BlitzGame(config["size"], config["blitz_time"]).play()
            print(f"Blitz mode with time limit: {config['bTime']} minutes")

        case parser.GameMode.CONTEST.value:
            print("Starting Contest Mode...")
            print(f"Loading contest from file: {config['cFile']}")

        case parser.GameMode.AI.value:
            print("Starting AI Mode...")
            print(f"AI plays as: {config['AIColor']}")

        case _:
            print("Unknown game mode. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()
