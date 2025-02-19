import sys
import othello.othello_board as board


def play():
    b = board.OthelloBoard(board.BoardSize.SIX_BY_SIX)
    current_player = board.Color.BLACK

    while True:
        no_black, no_white = False, False

        print(str(b))
        print(f"\n{current_player.name}'s turn ({current_player.value})")

        possible_moves = b.line_cap_move(current_player)
        if possible_moves.bits == 0:
            if current_player == board.Color.BLACK:
                no_black = True
            else:
                no_white = True

            if no_black and no_white:
                print("No valid moves for both players. Game over.")
            elif no_black:
                print("No valid moves for black. White wins!")
            elif no_white:
                print("No valid moves for white. Black wins!")
            else:
                print(
                    f"No valid moves for {current_player.name}. Skipping turn.")
                current_player = (
                    board.Color.WHITE if current_player == board.Color.BLACK else board.Color.BLACK
                )
                continue

            sys.exit(0)

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

        b.play(x_coord, y_coord)

        current_player = board.Color.WHITE if current_player == board.Color.BLACK else board.Color.BLACK
