"""Controllers for the Othello game."""

from __future__ import annotations
from random import choice
from abc import ABC, abstractmethod

import logging

from othello.ai_features import find_best_move
from othello.othello_board import (
    BoardSize,
    Color,
    GameOverException,
    IllegalMoveException,
    OthelloBoard,
)
from othello.parser import DEFAULT_BLITZ_TIME
import othello.logger as log

logger = logging.getLogger("Othello")


class Player:
    """
    Base class for a player in the game.
    """

    def __init__(self):
        """
        Player initialization.
        """
        self.controller = None
        self.color = None

    def attach(self, controller: GameController):
        """
        Attach a game controller to the player.

        :param controller: The game controller to attach
        :type controller: GameController
        """
        self.controller = controller

    def set_color(self, color: Color):
        """
        Set the color for this player.

        :param color: The color to assign to this player (BLACK or WHITE)
        :type color: Color
        """
        self.color = color

    def next_move(self):
        """
        Base method for determining the next move.
        Implemented by subclasses.
        """
        pass


class HumanPlayer(Player):
    """
    Player class representing a human player.
    Triggers the human play callback when it's time to make a move.
    """

    def next_move(self):
        """
        Signal that it's time for the human player to make a move.
        Calls the human_play_callback if it has been set in the controller.

        :raises Exception: if the controller is not defined.
        """
        if self.controller is None:
            raise Exception("controller not defined")
        if self.controller.human_play_callback is not None:
            self.controller.human_play_callback()


class RandomPlayer(Player):
    """
    Player class that makes random moves selected from available legal moves.
    """

    def next_move(self):
        """
        Choose a random legal move and play it on the board.

        :raises Exception: If controller or color is not defined
        :raises GameOverException: If the game is over
        """
        if self.controller is None:
            raise Exception("controller not defined")
        if self.color is None:
            raise Exception("color is not defined")
        move = choice(
            self.controller.get_possible_moves(self.color).hot_bits_coordinates()
        )
        try:
            self.controller.play(move[0], move[1])
        except GameOverException:
            raise


class AIPlayer(Player):
    """
    Player class that uses AI algorithms to determine the next move.
    """

    def __init__(
        self,
        board: OthelloBoard,
        depth: int = 3,
        algorithm: str = "minimax",
        heuristic: str = "coin_parity",
    ):
        """
        Initialize an AI player.

        :param board: The Othello game board
        :type board: OthelloBoard
        :param depth: The depth of the search algorithm, defaults to 3
        :type depth: int, optional
        :param algorithm: The search algorithm to use, defaults to "minimax"
        :type algorithm: str, optional
        :param heuristic: The heuristic function to evaluate board positions, defaults to "coin_parity"
        :type heuristic: str, optional
        """
        self.board = board
        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic

    def next_move(self):
        """
        Determine the best move using specified AI algorithm and heuristic,
        then play it on the board.

        :raises Exception: if the controller is not defined
        """
        if self.controller is None:
            raise Exception("controller not defined")
        move = find_best_move(
            self.board, self.depth, self.color, self.algorithm, self.heuristic
        )
        self.controller.play(move[0], move[1])


class Player(ABC):
    def __init__(self):
        self.controller = None
        self.color = None

    def attach(self, controller: GameController):
        self.controller = controller

    def set_color(self, color: Color):
        self.color = color

    @abstractmethod
    def next_move(self):
        if self.controller is None:
            raise Exception("controller not defined")


class HumanPlayer(Player):
    def next_move(self):
        super().next_move()
        if self.controller.human_play_callback is not None:
            self.controller.human_play_callback()


class RandomPlayer(Player):
    def next_move(self):
        super().next_move()
        if self.color is None:
            raise Exception("color is not defined")
        move = choice(
            self.controller.get_possible_moves(self.color).hot_bits_coordinates()
        )
        self.controller.play(move[0], move[1])


class AIPlayer(Player):
    def __init__(
        self,
        board: OthelloBoard,
        depth: int = 3,
        algorithm: str = "minimax",
        heuristic: str = "coin_parity",
        benchmark: bool = False,
    ):
        self.board = board
        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.benchmark = benchmark

    def next_move(self):
        super().next_move()
        move = find_best_move(
            self.board,
            self.depth,
            self.color,
            self.algorithm,
            self.heuristic,
            self.benchmark,
        )
        self.controller.play(move[0], move[1])


class GameController:
    """
    Initialize the game controller.

    :param board: The Othello game board
    :param blitz_mode: If True, the game is in blitz mode and the time limit is used
    :param time_limit: The time limit for blitz mode
    """

    def __init__(
        self,
        board: OthelloBoard,
        black_player,
        white_player,
        blitz_mode=False,
        time_limit=None,
    ):
        """
        Initialize the game controller.

        :param board: The Othello game board
        :param blitz_mode: If True, the game is in blitz mode and the time limit is used
        :param time_limit: The time limit for blitz mode
        """
        logger.debug("Initializing controller in GameController, from controllers.py.")
        self._board = board
        self.size = board.size
        self.first_player_human = True
        self.post_play_callback = None
        self.is_blitz = blitz_mode
        self.time_limit = time_limit if time_limit is not None else DEFAULT_BLITZ_TIME
        black_player.attach(self)
        self.human_play_callback = None
        self.post_play_callback = None
        black_player.set_color(Color.BLACK)
        white_player.attach(self)
        white_player.set_color(Color.WHITE)
        self.players = {Color.BLACK: black_player, Color.WHITE: white_player}

    def next_move(self):
        """
        Call the next_move method of the player whose turn it currently is.
        """
        self.players[self._board.current_player].next_move()

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

    def get_last_play(self):
        """
        Get the coordinates of the last played move.

        :return: A tuple containing the bitboards of each player, the x and y
        coordinates of the last move, and the color of the associated player
        :rtype: tuple[Bitboard, Bitboard, int, int, Color]
        """
        return self._board.get_last_play()

    def popcount(self, color: Color):
        """
        Count the number of pieces of the specified color on the board.

        :param color: The color of pieces to count
        :type color: Color
        :return: The number of pieces of the specified color on the board
        :rtype: int
        """
        return (
            self._board.black.popcount()
            if color is Color.BLACK
            else self._board.white.popcount()
        )

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

    def current_player_is_human(self):
        """
        Check if the current player is a human player.

        :return: True if the current player is a human player, False otherwise
        :rtype: bool
        """
        return isinstance(self.players[self._board.current_player], HumanPlayer)

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
        super().__init__(board)
        logger.debug("   Controller for Random Player.")
        self._random_player_color = random_player_color
        self.first_player_human = random_player_color is not Color.BLACK

    def ready(self):
        if self._random_player_color is Color.BLACK:
            logger.debug("Random player is ready to play.")
            self._play()

    def _play(self):
        move = choice(
            self.get_possible_moves(self._random_player_color).hot_bits_coordinates()
        )
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
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
        super().__init__(board)
        logger.debug("   Controller for AI Player.")

        if isinstance(ai_color, str):
            if ai_color == "X":
                self.ai_color = Color.BLACK
            elif ai_color == "O":
                self.ai_color = Color.WHITE
            else:
                self.ai_color = ai_color
        elif not isinstance(ai_color, Color):
            log.log_error_message(
                ValueError, "Invalid ai_color type: {type(ai_color)}."
            )
            raise ValueError(
                f"Invalid ai_color type: {type(ai_color)}. Must be a string or Color enum."
            )

        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic
        self.random_player = random_player

    def ready(self):
        if self.ai_color is self._board.current_player:
            logger.debug("AI player is ready to play.")
            self._play()

    def _play(self):
        move = find_best_move(
            self._board, self.depth, self.ai_color, self.algorithm, self.heuristic
        )
        self.play(move[0], move[1])

    def play(self, x_coord: int, y_coord: int):
        self._board.play(x_coord, y_coord)
        if self.post_play_callback is not None:
            self.post_play_callback()
        if self._board.current_player is self.ai_color:
            self._play()
