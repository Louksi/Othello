"""
Implementation of the blitz timer that's used to give both players
a maximum time for all their plays (individually)
"""
from time import time
import logging
import othello.logger as log
from othello.othello_board import Color

# init: timeLimit (in minutes)
# startTime,
# totalTime (in seconds),
# remainingTime,
# currentPlayer

# def startTimer(player)
# def pauseTimer()
# def changePlayer(player)
# def getRemainingTime(player)
# def isTimeUp(player)

# def displayTime()

logger = logging.getLogger("Othello")


class BlitzTimer:
    """
    The actual timer
    """

    def __init__(self, time_limit) -> None:
        """
        Initializes a BlitzTimer object.

        Args:
            timeLimit (int): The time limit, in minutes.
        """
        logger.debug(
            f"Entering init from blitz_timer.py." f"Initializing BlitzTimer with time_limit: {time_limit} minutes.")
        self.start_time = None
        # converts the time limit from minutes to seconds
        self.total_time = time_limit * 60
        self.remaining_time = {
            'black': self.total_time,
            'white': self.total_time
        }
        self.current_player = None
        logger.debug(
            f"   BlitzTimer initialized with {self.total_time} seconds per player.")

    def start_timer(self, player) -> None:
        """
        Starts the BlitzTimer for the given player.

        Args:
            player (str): The player to start the timer for, either 'black' or 'white'.
        """
        logger.debug(
            f"Entering start_time from blitz_timer.py." f"Starting timer for player: {player}.")
        self.start_time = time()
        self.current_player = player

    def pause_timer(self) -> None:
        """
        Pauses the BlitzTimer and updates the remaining time for the current player.

        If the BlitzTimer is not running, does nothing.
        """
        logger.debug(
            f"Entering pause_timer from blitz_timer.py for player: {self.current_player}.")
        if self.start_time and self.current_player:
            base_time = self.remaining_time[self.current_player]
            elapsed_time = (time() - self.start_time)
            self.remaining_time[self.current_player] = max(
                0, base_time - elapsed_time)
            logger.debug(
                f"   Timer paused for {self.current_player}. Elapsed: {elapsed_time:.2f}s, " f"Remaining time updated from {base_time:.2f}s to {self.remaining_time[self.current_player]:.2f}s.")
            self.start_time = None
            self.current_player = None
        else:
            logger.debug("   Timer not running.")

    def change_player(self, player) -> None:
        """
        Changes the current player and pauses the BlitzTimer if it was running.

        Args:
            player (str): The new current player, either 'black' or 'white'.
        """
        logger.debug(
            f"Entering change_player from blitz_timer.py." f"Changing player from {self.current_player} to {player}.")
        self.pause_timer()
        self.start_timer(player)

    def get_remaining_time(self, player) -> float:
        """
        Returns the remaining time for the given player.

        If the BlitzTimer is running for the given player, updates the remaining time
        by subtracting the elapsed time since the last call to startTimer or changePlayer.

        Args:
            player (str): The player to get the remaining time for, either 'black' or 'white'.

        Returns:
            float: The remaining time in seconds.
        """
        logger.debug(
            f"Entering get_remaining_time from blitz_timer.py." f"Getting remaining time for player: {player}.")
        if self.start_time and player == self.current_player:
            base_time = self.remaining_time[player]
            elapsed_time = (time() - self.start_time)
            self.remaining_time[player] = max(
                0, base_time - elapsed_time)
            logger.debug(
                f"   Updated remaining time for {player} from {base_time:.2f}s to {self.remaining_time[player]:.2f}s " f"(elapsed: {elapsed_time:.2f}s).")
        else:
            logger.debug(
                f"   Returning cached remaining time for {player}: {self.remaining_time[player]:.2f}s.")
        return self.remaining_time[player]

    def is_time_up(self, player) -> bool:
        """
        Checks if the time is up for the given player.

        Args:
            player (str): The player to check, either 'black' or 'white'.

        Returns:
            bool: True if the time is up, False otherwise.
        """
        logger.debug(
            f"Entering is_time_up from blitz_timer.py for player: {player}.")
        return self.get_remaining_time(player) <= 0

    def time_player(self, player: Color):
        logger.debug(
            f"Entering time_player from blitz_timer.py" f"Converting time for player: {player}.")
        p_time = int(self.get_remaining_time(
            "black" if player is Color.BLACK else "white"))

        p_time_minutes = p_time // 60
        p_time_seconds = p_time % 60
        logger.debug(
            f"   Time for {player}: {p_time_minutes}:{p_time_seconds:02d}.")
        return (p_time_minutes, p_time_seconds)

    def display_time_player(self, player: Color):
        logger.debug("Entering display_time_player from blitz_timer.py.")
        p_time = self.time_player(player)
        return f"{p_time[0]:02d}:{p_time[1]:02d}"

    def display_time(self) -> str:
        """
        Displays the remaining time for both players in a formatted string.

        The time for each player is calculated in minutes and seconds, and returned as a string
        in the format "MM:SS" for both black and white players.

        Returns:
            str: A formatted string showing the remaining time for both players.
        """
        logger.debug("Entering display_time from blitz_timer.py.")
        black_time = self.time_player(Color.BLACK)
        white_time = self.time_player(Color.WHITE)

        black_time_minutes, black_time_seconds = black_time
        white_time_minutes, white_time_seconds = white_time

        black_print = f"Black Time: {black_time_minutes:02d}:{black_time_seconds:02d}\n"
        white_print = f"White Time: {white_time_minutes:02d}:{white_time_seconds:02d}\n"
        return f"{black_print}{white_print}"
