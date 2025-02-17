import sys
import othello.parser as parser
import othello.othello_board as board


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
        case parser.GameMode.NORMAL:
            b = board.OthelloBoard(board.BoardSize.SIX_BY_SIX)
            current_player = board.Color.BLACK

            while True:
                print(str(b))
                print(f"\n{current_player.name}'s turn ({current_player.value})")

                possible_moves = b.line_cap_move(current_player)
                if possible_moves.bits == 0:
                    print(
                        f"No valid moves for {current_player.name}. Skipping turn.")
                    current_player = board.Color.WHITE if current_player == board.Color.BLACK else board.Color.BLACK
                    continue

                print("Possible moves: ")
                for y in range(b.size.value):
                    for x in range(b.size.value):
                        if possible_moves.get(x, y):
                            print(f"{chr(ord('a')+x)}{y+1}", end=" ")
                print()

                move = input("Enter your move: ").strip().lower()

                if len(move) < 2 or move[0] not in "abcdef"[:b.size.value] or not move[1:].isdigit():
                    print("Invalid move format. Try again.")
                    continue

                x_coord = ord(move[0]) - ord('a')
                y_coord = int(move[1]) - 1

                if not possible_moves.get(x_coord, y_coord):
                    print("Invalid move. Not a legal play. Try again.")
                    continue

                captures = b.line_cap(x_coord, y_coord, current_player)

                if current_player == board.Color.BLACK:
                    b.black |= captures
                else:
                    b.white |= captures

                current_player = board.Color.WHITE if current_player == board.Color.BLACK else board.Color.BLACK

        case parser.GameMode.BLITZ:
            print("Starting Blitz Mode...")
            game = parser.BlitzMode(parser.BoardSize(config["size"]))
            game.time_limit = config["bTime"]
            print(f"Blitz mode with time limit: {game.time_limit} minutes")

        case parser.GameMode.CONTEST:
            print("Starting Contest Mode...")
            print(f"Loading contest from file: {config['cFile']}")

        case parser.GameMode.AI:
            print("Starting AI Mode...")
            print(f"AI plays as: {config['AIColor']}")

        case _:
            print("Unknown game mode. Exiting.")
            sys.exit(1)


if __name__ == "__main__":
    main()
