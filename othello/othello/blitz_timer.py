"""
Implementation of the blitz timer that's used to give both players
a maximum time for all their plays (individually)
"""
from time import time

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
        self.start_time = None
        # converts the time limit from minutes to seconds
        self.total_time = time_limit * 60
        self.remaining_time = {
            'black': self.total_time,
            'white': self.total_time
        }
        self.current_player = None

    def start_timer(self, player) -> None:
        """
        Starts the BlitzTimer for the given player.

        Args:
            player (str): The player to start the timer for, either 'black' or 'white'.
        """
        self.start_time = time()
        self.current_player = player

    def pause_timer(self) -> None:
        """
        Pauses the BlitzTimer and updates the remaining time for the current player.

        If the BlitzTimer is not running, does nothing.
        """
        if self.start_time and self.current_player:
            self.remaining_time[self.current_player] = max(
                0, self.remaining_time[self.current_player] - (time() - self.start_time))
            self.start_time = None
            self.current_player = None

    def change_player(self, player) -> None:
        """
        Changes the current player and pauses the BlitzTimer if it was running.

        Args:
            player (str): The new current player, either 'black' or 'white'.
        """
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
        if self.start_time and player == self.current_player:
            self.remaining_time[player] = max(
                0, self.remaining_time[player] - (time() - self.start_time))
        return self.remaining_time[player]

    def is_time_up(self, player) -> bool:
        """
        Checks if the time is up for the given player.

        Args:
            player (str): The player to check, either 'black' or 'white'.

        Returns:
            bool: True if the time is up, False otherwise.
        """
        return self.get_remaining_time(player) <= 0

    def display_time(self) -> str:
        """
        Displays the remaining time for both players in a formatted string.

        The time for each player is calculated in minutes and seconds, and returned as a string
        in the format "MM:SS" for both black and white players.

        Returns:
            str: A formatted string showing the remaining time for both players.
        """

        black_time = int(self.get_remaining_time('black'))
        white_time = int(self.get_remaining_time('white'))

        black_time_minutes = black_time // 60
        white_time_minutes = white_time // 60

        black_time_seconds = black_time % 60
        white_time_seconds = white_time % 60

        black_print = f"Black Time: {black_time_minutes:02d}:{black_time_seconds:02d}\n"
        white_print = f"White Time: {white_time_minutes:02d}:{white_time_seconds:02d}\n"
        return f"{black_print}{white_print}"
