import pytest
from time import time, sleep
import unittest
from othello.blitzTimer import BlitzTimer

TEST_TIME = 0.1
PLAYER1 = 'black'
PLAYER2 = 'white'


# TEST INITIALIZATION

def test_init():
    timer = BlitzTimer(TEST_TIME)
    assert timer.startTime == None
    assert timer.totalTime == TEST_TIME * 60
    assert timer.remainingTime['black'] == TEST_TIME * 60
    assert timer.remainingTime['white'] == TEST_TIME * 60
    assert timer.currentPlayer == None


# TEST STARTING

def test_starting():
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    assert timer.startTime is not None
    assert timer.currentPlayer == PLAYER1
    assert timer.remainingTime['black'] == TEST_TIME * 60
    assert timer.remainingTime['white'] == TEST_TIME * 60


# TEST PAUSING

def test_pausing():
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    timer.pauseTimer()
    assert timer.startTime is None
    assert timer.remainingTime[PLAYER1] < TEST_TIME * 60
    assert timer.currentPlayer == None


# TEST SWITCHING

def test_switching():
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    timer.changePlayer(PLAYER2)
    assert timer.remainingTime[PLAYER1] < TEST_TIME * 60
    assert timer.currentPlayer == PLAYER2
    assert timer.startTime is not None
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60


# TEST REMAINING

def test_remaining():
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
    timer = BlitzTimer(TEST_TIME)
    timer.startTimer(PLAYER1)
    sleep(TEST_TIME * 60)
    assert timer.getRemainingTime(PLAYER1) == 0
    assert timer.getRemainingTime(PLAYER2) == TEST_TIME * 60
    assert timer.remainingTime[PLAYER1] == 0
    assert timer.remainingTime[PLAYER2] == TEST_TIME * 60
    assert timer.isTimeUp(PLAYER1) == True
    assert timer.isTimeUp(PLAYER2) == False
