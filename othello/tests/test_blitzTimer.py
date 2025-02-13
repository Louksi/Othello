import pytest
from time import time, sleep
import unittest
from othello.blitzTimer import BlitzTimer

TEST_TIME = 0.1
PLAYER1 = 'black'
PLAYER2 = 'white'


# TEST INITIALIZATION

def test_init():
    """
    Tests the initialization of the BlitzTimer class.

    Asserts that:
     - the start time is None
     - the total time is the given time in seconds
     - the remaining time is the same as the total time for both players
     - the current player is None
    """
    timer = BlitzTimer(TEST_TIME)
    assert timer.startTime == None
    assert timer.totalTime == TEST_TIME * 60
    assert timer.remainingTime['black'] == TEST_TIME * 60
    assert timer.remainingTime['white'] == TEST_TIME * 60
    assert timer.currentPlayer == None


# TEST STARTING

def test_starting():
    """
    Tests starting the BlitzTimer class.

    Asserts that:
     - the start time is not None
     - the current player is the one given
     - the remaining time is the same as the total time for the given player
     - the remaining time is the same as the total time for the other player
    """

    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    assert timer.startTime is not None
    assert timer.currentPlayer == PLAYER1
    assert timer.remainingTime['black'] == TEST_TIME * 60
    assert timer.remainingTime['white'] == TEST_TIME * 60


# TEST PAUSING

def test_pausing():
    """
    Tests pausing the BlitzTimer class.

    Asserts that:
     - the start time is None
     - the remaining time is less than the total time for the current player
     - the current player is None
    """
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    timer.pauseTimer()
    assert timer.startTime is None
    assert timer.remainingTime[PLAYER1] < TEST_TIME * 60
    assert timer.currentPlayer == None


# TEST SWITCHING

def test_switching():
    """
    Tests switching the BlitzTimer class.

    Asserts that:
     - the remaining time for the first player is less than the total time
     - the current player is the second player
     - the start time is not None
     - the remaining time for the second player is the same as the total time
    """
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    timer.changePlayer(PLAYER2)
    assert timer.remainingTime[PLAYER1] < TEST_TIME * 60
    assert timer.currentPlayer == PLAYER2
    assert timer.startTime is not None
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60


# TEST REMAINING

def test_remaining():
    """
    Tests the remaining time of the BlitzTimer class.

    Asserts that:
     - the remaining time for the first player is the same as the total time
     - the remaining time for the second player is the same as the total time
     - after some time has passed, the remaining time for the first player is less than the total time
     - after some time has passed, the remaining time for the second player is the same as the total time
     - after the time is up, the remaining time for the first player is 0
     - after the time is up, the remaining time for the second player is the same as the total time
    """
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    assert timer.remainingTime[PLAYER1] == TEST_TIME * 60
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60
    sleep(1)
    assert timer.getRemainingTime(PLAYER1) < TEST_TIME * 60
    assert timer.getRemainingTime(PLAYER2) == TEST_TIME * 60
    assert timer.remainingTime[PLAYER1] < TEST_TIME * 60
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60

    # time is up
    sleep(TEST_TIME * 60)
    assert timer.getRemainingTime(PLAYER1) == 0
    assert timer.getRemainingTime(PLAYER2) == TEST_TIME * 60
    assert timer.remainingTime[PLAYER1] == 0
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60


# TEST TIME IS UP

def test_timeUp():
    """
    Tests the isTimeUp function of the BlitzTimer class.

    This test ensures that after the time limit has elapsed for PLAYER1:
     - The remaining time for PLAYER1 is 0.
     - The remaining time for PLAYER2 is the initial total time.
     - The isTimeUp function returns True for PLAYER1.
     - The isTimeUp function returns False for PLAYER2.
    """

    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    sleep(TEST_TIME * 60)
    assert timer.getRemainingTime(PLAYER1) == 0
    assert timer.getRemainingTime(PLAYER2) == TEST_TIME * 60
    assert timer.remainingTime[PLAYER1] == 0
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60
    assert timer.isTimeUp(PLAYER1) == True
    assert timer.isTimeUp(PLAYER2) == False
