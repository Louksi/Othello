from random import choice

from othello.ai_features import find_best_move
from othello.othello_board import BoardSize, Color, OthelloBoard
from othello.parser import DEFAULT_BLITZ_TIME


class GameController:
    def __init__(self, board: OthelloBoard, blitz_mode=False, time_limit=None):
        """
        Initialize the game controller.

        :param board: The Othello game board
        :param blitz_mode: If True, the game is in blitz mode and the time limit is used
        :param time_limit: The time limit for blitz mode
        """
        self._board = board
        self.size = board.size
        self.first_player_human = True
        self.post_play_callback = None
        self.is_blitz = blitz_mode
        self.time_limit = time_limit if time_limit is not None else DEFAULT_BLITZ_TIME

    def ready(self):
        """
        Prepare the game controller for the start of the game.

        This method is called once before the game starts and must be called
        before any other method of this class is called.
        """
        pass

    def play(self, x_coord: int, y_coord: int):
        """
        Make a move on the board.

        This method changes the state of the board to reflect the move given by
        x_coord and y_coord. If a callback was registered using the
        set_post_play_callback method, it is called after the move is made.

        :param x_coord: The x coordinate of the move (0 indexed)
        :param y_coord: The y coordinate of the move (0 indexed)
        """
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()

    def get_possible_moves(self, player: Color):
        """
        Return a Bitboard of the possible moves for the given player.

        :param player: The player for which to get the possible moves
        :return: A Bitboard of the possible moves for the given player
        """
        return self._board.line_cap_move(player)

    def get_position(self, player: Color, x_coord: int, y_coord: int):
        """
        Get the state of the specified position on the board for a given player.

        This method checks whether a given board position is occupied by the player's piece.

        :param player: The player whose piece state is being queried.
        :type player: Color
        :param x_coord: The x coordinate of the position on the board (0 indexed).
        :type x_coord: int
        :param y_coord: The y coordinate of the position on the board (0 indexed).
        :type y_coord: int
        :return: True if the player's piece occupies the position, False otherwise.
        :rtype: bool
        """

        to_query = self._board.black if player is Color.BLACK else self._board.white
        return to_query.get(x_coord, y_coord)

    def restart(self):
        """
        Restart the game to its initial state.

        This method resets the game board to the starting configuration,
        clearing any history and setting the current player to the initial player.
        """

        self._board.restart()

    def get_turn_number(self):
        """
        Get the current turn number of the game.

        The turn number is a unique identifier for the current state of the game
        that increments every time a move is made. The first turn is turn number 1,
        and the number increments by one for each subsequent turn.

        :return: The current turn number of the game
        :rtype: int
        """
        return self._board.get_turn_id()

    def is_game_over(self):
        """
        Check whether the game is in a game over state.

        The game is in a game over state when either player has no valid moves
        available, or the board is completely full. When the game is in a game
        over state, a winner can be determined by counting the number of pieces
        on the board of each color.

        :return: True if the game is in a game over state, False otherwise.
        :rtype: bool
        """
        return self._board.is_game_over()

    def get_current_player(self):
        """
        Get the current player.

        This method returns the current player of the game. The first player is
        black, and the second player is white.

        :return: The current player of the game
        :rtype: Color
        """
        return self._board.current_player

    def get_pieces_count(self, player_color: Color):
        """
        Get the count of pieces on the board for the given player color.

        This method returns the number of pieces currently on the board
        for the specified player color (black or white).

        :param player_color: The color of the player whose pieces count is to be retrieved.
        :type player_color: Color
        :return: The count of pieces on the board for the specified player color.
        :rtype: int
        """

        return (
            self._board.black.popcount()
            if player_color is Color.BLACK
            else self._board.white.popcount()
        )

    def get_history(self):
        """
        Get the history of the game.

        This method returns a tuple containing the move history of the game. Each
        element of the tuple is a tuple of two elements. The first element is a
        tuple of two integers representing the x and y coordinates of the move,
        and the second element is a Color object representing the player that made
        the move (black or white).

        :return: The history of the game
        :rtype: tuple[tuple[int, int], Color]
        """
        return self._board.get_history()

    def export(self):
        """
        Export the game state to a string.

        This method returns a string representation of the current state of the game,
        including the board and the move history. The returned string is formatted
        according to the Othello save file format.

        :return: The game state as a string
        :rtype: str
        """

        return self._board.export()

    def export_history(self):
        """
        Export the move history of the game to a string.

        This method returns a string representation of the move history of the game,
        formatted according to the Othello save file format.

        :return: The move history of the game as a string
        :rtype: str
        """
        return self._board.export_history()

    def __str__(self):
        """
        Return a string representation of the game state.

        This method returns a string representation of the current state of the game,
        including the board and the move history. The returned string is formatted
        according to the Othello save file format.

        :return: The game state as a string
        :rtype: str
        """
        return str(self._board)


class RandomPlayerGameController(GameController):
    def __init__(self, board: OthelloBoard, random_player_color: Color):
        """
        Initialize the RandomPlayerGameController.

        This method initializes a new instance of the RandomPlayerGameController class.

        :param board: The OthelloBoard to play on
        :param random_player_color: The color of the player that will make random moves
        :type random_player_color: Color
        """

        super().__init__(board)
        self._random_player_color = random_player_color
        self.first_player_human = random_player_color is not Color.BLACK

    def ready(self):
        """
        Prepare the RandomPlayerGameController for the start of the game.

        If the random player is set to play as black, this method will
        automatically initiate a move for the black player.
        """

        if self._random_player_color is Color.BLACK:
            self._play()

    def _play(self):
        """
        Make a random move on the board as the random player.

        This method randomly selects a valid move for the random player and makes
        the move on the board. This method is called automatically when the game
        starts if the random player is set to play as black, and after each move
        by the human player. The game continues until the game is in a game over
        state.

        :return: None
        :rtype: None
        """
        move = choice(
            self.get_possible_moves(self._random_player_color).hot_bits_coordinates()
        )
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        """
        Make a move on the board.

        This method is used to make a move on the board. It delegates to the play method
        of the underlying OthelloBoard and then calls the post-play callback if it has
        been set using the set_post_play_callback method. If the random player is set
        to play, this method will also automatically initiate a move by the random
        player after each move by the human player.

        :param x_coord: The x coordinate of the move (0 indexed)
        :param y_coord: The y coordinate of the move (0 indexed)
        :return: None
        :rtype: None
        """
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()
        if self._board.current_player is self._random_player_color:
            self._play()


class AIPlayerGameController(GameController):
    def __init__(
        self,
        board: OthelloBoard,
        ai_color: Color = Color.BLACK,
        depth: int = 3,
        algorithm: str = "minimax",
        heuristic: str = "coin_parity",
        random_player: bool = False,
    ):
        """
        Initialize an AIPlayerGameController.

        :param board: The OthelloBoard to play on.
        :type board: OthelloBoard
        :param ai_color: The color that the AI will play as. Defaults to Color.BLACK.
        :type ai_color: Color or str
        :param depth: The maximum depth to explore the game tree. Defaults to 3.
        :type depth: int
        :param algorithm: The search algorithm to use. Defaults to "minimax".
        :type algorithm: str
        :param heuristic: The heuristic function to use. Defaults to "coin_parity".
        :type heuristic: str
        :param random_player: Whether the AI should play randomly. Defaults to False.
        :type random_player: bool
        :raises ValueError: If the ai_color is invalid.
        """
        super().__init__(board)

        if isinstance(ai_color, str):
            if ai_color == "X":
                self.ai_color = Color.BLACK
            elif ai_color == "O":
                self.ai_color = Color.WHITE
            else:
                self.ai_color = ai_color
        elif not isinstance(ai_color, Color):
            raise ValueError(
                f"Invalid ai_color type: {type(ai_color)}. Must be a string or Color enum."
            )

        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.random_player = random_player

    def ready(self):
        """
        Prepare the AIPlayerGameController for the start of the game.

        If the AI player's color matches the current player on the board, this
        method will automatically initiate a move for the AI player.

        :return: None
        :rtype: None
        """

        if self.ai_color is self._board.current_player:
            self._play()

    def _play(self):
        """
        Find the best move according to the AI's settings and play it.

        This method is called by the ready method if the AI player's color matches
        the current player on the board. It uses the find_best_move function to
        determine the best move according to the AI's settings, and then plays the
        move on the board.

        :return: None
        :rtype: None
        """
        move = find_best_move(
            self._board, self.depth, self.ai_color, self.algorithm, self.heuristic
        )
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        """
        Make a move on the board.

        This method changes the state of the board to reflect the move given by
        x_coord and y_coord. If a callback was registered using the
        set_post_play_callback method, it is called after the move is made.
        Additionally, if the AI player's color matches the current player on the
        board, this method will automatically initiate a move for the AI player.

        :param x_coord: The x coordinate of the move (0 indexed)
        :param y_coord: The y coordinate of the move (0 indexed)
        :return: None
        :rtype: None
        """
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()
        if self._board.current_player is self.ai_color:
            self._play()
