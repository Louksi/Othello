from othello.othello_bitboard import OthelloBitboard, BoardSize, Color
import othello.parser as parser


class ContestMode:
    def __init__(self, filename):
        if parser.GameMode.CONTEST:
            self.filename = filename
            self.board = None
            self.current_turn = None
            self.load_game_state()

    def load_game_state(self):
        """Loads the game state from a save file and initializes the board."""
        with open(self.filename, "r") as file:
            lines = file.readlines()

        # First line: Board size
        board_size = int(lines[0].strip())
        self.board = OthelloBitboard(BoardSize(board_size))

        # Second line: Current turn
        self.current_turn = Color.BLACK if lines[1].strip(
        ) == "X" else Color.WHITE

        # Remaining lines: Board state
        for y, line in enumerate(lines[2:]):
            for x, char in enumerate(line.strip().split()):
                if char == "X":
                    self.board.black.set(x, y, True)
                elif char == "O":
                    self.board.white.set(x, y, True)

    def switch_turn(self):
        """Switches the turn between players."""
        self.current_turn = Color.BLACK if self.current_turn == Color.WHITE else Color.WHITE

    def play_move(self, x, y):
        """
        Plays a move at (x, y) for the current player.
        Flips pieces using the `line_cap` method and updates the board state.
        """
        if not self.is_valid_move(x, y):
            raise ValueError("Invalid move")

        bitboard = self.board.black if self.current_turn == Color.BLACK else self.board.white
        flipped = self.board.line_cap(x, y, self.current_turn)

        # Set the played move
        bitboard.set(x, y, True)

        # Apply captured pieces
        for i in range(self.board.size.value):
            for j in range(self.board.size.value):
                if flipped.get(i, j):
                    self.board.black.set(
                        i, j, self.current_turn == Color.BLACK)
                    self.board.white.set(
                        i, j, self.current_turn == Color.WHITE)

        self.switch_turn()

    def is_valid_move(self, x, y):
        """Checks if a move is valid using `line_cap_move`."""
        return self.board.line_cap_move(self.current_turn).get(x, y)

    def __str__(self):
        return f"Current Turn: {self.current_turn.value}\n{self.board}"
