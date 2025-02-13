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
        self.startTime = None
        self.totalTime = timeLimit * 60  # converts the time limit from minutes to seconds
        self.remainingTime = {
            'black': self.totalTime,
            'white': self.totalTime
        }
        self.currentPlayer = None

    def startTimer(self, player) -> None:
        self.startTime = time()
        self.currentPlayer = player

    def pauseTimer(self) -> None:
        if self.startTime and self.currentPlayer:
            self.remainingTime[self.currentPlayer] = max(
                0, self.remainingTime[self.currentPlayer] - (time() - self.startTime))
            self.startTime = None
            self.currentPlayer = None

    def changePlayer(self, player) -> None:
        self.pauseTimer()
        self.startTimer(player)

    def getRemainingTime(self, player) -> float:
        if self.startTime and player == self.currentPlayer:
            self.remainingTime[player] = max(
                0, self.remainingTime[player] - (time() - self.startTime))
        return self.remainingTime[player]

    def isTimeUp(self, player) -> bool:
        return self.getRemainingTime(player) <= 0

    def displayTime(self) -> None:
        blackTime = int(self.getRemainingTime('black'))
        whiteTime = int(self.getRemainingTime('white'))

        BMins = blackTime // 60
        WMins = whiteTime // 60

        BSecs = blackTime % 60
        WSecs = whiteTime % 60

        return f"Black Time: {BMins:02d}:{BSecs:02d}\nWhite Time: {WMins:02d}:{WSecs:02d}\n"
