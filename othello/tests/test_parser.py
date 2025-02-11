import pytest
import sys
from othello.parser import parse_args, GameMode, createParser, aiColor

# TEST DEFAULT CONFIGURATION


def test_defaultConfig(monkeypatch):

    # get the default config dictionary (hard coded here?)
    # for now we do with 4 args but
    # the idea is to get the config from parser,
    # and check if both dicts are the same.

    monkeypatch.setattr(sys, 'argv', ["othello"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.NORMAL
    assert parseConfig["filename"] is None
    assert parseConfig["size"] == 8
    assert parseConfig["debug"] is False


# TEST REGULAR OPTIONS

# file
def test_file(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "dummyGame.txt"])
    mode, parseConfig = parse_args()
    assert parseConfig["filename"] == "dummyGame.txt"

    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys, 'argv', ["othello", "dummyGame.txt", "-a", "s"])
        _, parseConfig = parse_args()


# help


def test_help(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-h"])
        parse_args()

# version


def test_version(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-v"])
        parse_args()


# debug

def test_debug(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-d"])
    mode, parseConfig = parse_args()

    assert parseConfig["debug"] is True

# size


def test_size(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-s", "10"])
    mode, parseConfig = parse_args()

    assert parseConfig["size"] == 10


# TEST MODES

# blitz mode
def test_blitzMode(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-b"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.BLITZ
    assert parseConfig["bTime"] == 30

    monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "60"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.BLITZ
    assert parseConfig["bTime"] == 60


# contest
def test_contestMode(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-c", "dummyGame.txt"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.CONTEST
    assert parseConfig["cFile"] == "dummyGame.txt"

# ai


def test_aiMode(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ["othello", "-a"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.AI
    assert parseConfig["aiColor"] == aiColor.BLACK.value

    monkeypatch.setattr(sys, 'argv', ["othello", "-aO"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.AI
    assert parseConfig["aiColor"] == aiColor.WHITE.value

    monkeypatch.setattr(sys, 'argv', ["othello", "-aA"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.AI
    assert parseConfig["aiColor"] == aiColor.ALL.value


# TEST ERRORS

# incorrect option
def test_errOption(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "--invalid"])
        parse_args()


# mode incompatibility
def test_errIncompModes(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys, 'argv', ["othello", "-b", "-c", "dummyGame.txt"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys, 'argv', ["othello", "-c", "dummyGame.txt", "-ai"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-a", "-b"])
        parse_args()


# incorrect size
def test_errSize(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-s", "3"])
        parse_args()


# incorrect blitz time
def test_errTime(monkeypatch):  # trouver le moyen de faire plusieurs tests
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "-20"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-t", "20"])
        parse_args()

# incorrect contest file


def test_errContest(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-c"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-c", ""])
        parse_args()

# incorrect ai color


def test_errColor(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-aB"])
        parse_args()

# incorrect ai color


def test_errAI(monkeypatch):
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-a[invalid]"])
        parse_args()
