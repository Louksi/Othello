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

    def __init__(self, timeLimit) -> None:
        """
        Initializes a BlitzTimer object.

        Args:
            timeLimit (int): The time limit, in minutes.
        """
        self.startTime = None
        self.totalTime = timeLimit * 60  # converts the time limit from minutes to seconds
        self.remainingTime = {
            'black': self.totalTime,
            'white': self.totalTime
        }
        self.currentPlayer = None

    def startTimer(self, player) -> None:
        """
        Starts the BlitzTimer for the given player.

        Args:
            player (str): The player to start the timer for, either 'black' or 'white'.
        """
        self.startTime = time()
        self.currentPlayer = player

    def pauseTimer(self) -> None:
        """
        Pauses the BlitzTimer and updates the remaining time for the current player.

        If the BlitzTimer is not running, does nothing.
        """
        if self.startTime and self.currentPlayer:
            self.remainingTime[self.currentPlayer] = max(
                0, self.remainingTime[self.currentPlayer] - (time() - self.startTime))
            self.startTime = None
            self.currentPlayer = None

    def changePlayer(self, player) -> None:
        """
        Changes the current player and pauses the BlitzTimer if it was running.

        Args:
            player (str): The new current player, either 'black' or 'white'.
        """
        self.pauseTimer()
        self.startTimer(player)

    def getRemainingTime(self, player) -> float:
        """
        Returns the remaining time for the given player.

        If the BlitzTimer is running for the given player, updates the remaining time
        by subtracting the elapsed time since the last call to startTimer or changePlayer.

        Args:
            player (str): The player to get the remaining time for, either 'black' or 'white'.

        Returns:
            float: The remaining time in seconds.
        """
        if self.startTime and player == self.currentPlayer:
            self.remainingTime[player] = max(
                0, self.remainingTime[player] - (time() - self.startTime))
        return self.remainingTime[player]

    def isTimeUp(self, player) -> bool:
        """
        Checks if the time is up for the given player.

        Args:
            player (str): The player to check, either 'black' or 'white'.

        Returns:
            bool: True if the time is up, False otherwise.
        """
        return self.getRemainingTime(player) <= 0

    def displayTime(self) -> None:
        """
        Displays the remaining time for both players in a formatted string.

        The time for each player is calculated in minutes and seconds, and returned as a string
        in the format "MM:SS" for both black and white players.

        Returns:
            str: A formatted string showing the remaining time for both players.
        """

        blackTime = int(self.getRemainingTime('black'))
        whiteTime = int(self.getRemainingTime('white'))

        BMins = blackTime // 60
        WMins = whiteTime // 60

        BSecs = blackTime % 60
        WSecs = whiteTime % 60

        return f"Black Time: {BMins:02d}:{BSecs:02d}\nWhite Time: {WMins:02d}:{WSecs:02d}\n"
