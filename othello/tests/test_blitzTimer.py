import pytest
from time import time
from unittest.mock import patch
from othello.blitzTimer import BlitzTimer

TEST_TIME = 2


# TEST INITIALIZATION

def test_init():
  timer = BlitzTimer(TEST_TIME)
  assert timer.startTime == None
  assert timer.totalTime == TEST_TIME * 60
  assert timer.remainingTime['black'] == TEST_TIME * 60
  assert timer.remainingTime['white'] == TEST_TIME * 60
  assert timer.currentPlayer == None


# TEST STARTING

# def test_starting():
#   timer = BlitzTimer(TEST_TIME)
#   with patch('time.time', return_value = 100):
#     timer.startTimer('black')
#     assert timer.startTime == 100
#     assert timer.currentPlayer == 'black'


# TEST PAUSING

# def test_pausing():
#   timer = BlitzTimer(TEST_TIME)
#   with patch('time.time', return_value = 100):
#     timer.startTimer('black')

#   with patch('time.time', return_value = 120): # 20 secs later
#     timer.pauseTimer()
#     assert timer.getRemainingTime('black') == TEST_TIME * 60 - 20
#     assert timer.startTime == None
#     assert timer.currentPlayer == None


# TEST SWITCHING


# TEST REMAINING


# TEST TIME IS UP

