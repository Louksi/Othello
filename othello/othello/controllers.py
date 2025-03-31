from __future__ import annotations
from random import choice
from abc import ABC, abstractmethod


from othello.ai_features import find_best_move
from othello.othello_board import (
    BoardSize,
    Color,
    GameOverException,
    IllegalMoveException,
    OthelloBoard,
)
from othello.parser import DEFAULT_BLITZ_TIME


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
    ):
        self.board = board
        self.depth = depth
        self.algorithm = algorithm
        self.heuristic = heuristic

    def next_move(self):
        super().next_move()
        move = find_best_move(
            self.board, self.depth, self.color, self.algorithm, self.heuristic
        )
        self.controller.play(move[0], move[1])


class GameController:
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
        return self._board.get_last_play()

    def popcount(self, color: Color):
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
