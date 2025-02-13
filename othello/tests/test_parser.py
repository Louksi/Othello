import pytest
import sys
from othello.parser import parse_args, GameMode, createParser, aiColor

# TEST DEFAULT CONFIGURATION


def test_defaultConfig(monkeypatch):

    # get the default config dictionary (hard coded here?)
    # for now we do with 4 args but
    # the idea is to get the config from parser,
    # and check if both dicts are the same.
    """
    Test the default configuration of the parser.

    When the parser is called without arguments, it should return the default
    configuration.
    """
    monkeypatch.setattr(sys, 'argv', ["othello"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.NORMAL
    assert parseConfig["filename"] is None
    assert parseConfig["size"] == 8
    assert parseConfig["debug"] is False


# TEST REGULAR OPTIONS

# file
def test_file(monkeypatch):
    """
    Test parsing of a game file.

    This test ensures that when a filename is provided as an argument,
    the parser correctly identifies the filename. It also checks that
    invalid combinations of arguments result in a SystemExit exception.
    """

    monkeypatch.setattr(sys, 'argv', ["othello", "dummyGame.txt"])
    mode, parseConfig = parse_args()
    assert parseConfig["filename"] == "dummyGame.txt"

    with pytest.raises(SystemExit):
        monkeypatch.setattr(
            sys, 'argv', ["othello", "dummyGame.txt", "-a", "s"])
        _, parseConfig = parse_args()


# help


def test_help(monkeypatch):
    """
    Test the help option.

    This test ensures that when the -h option is provided, the parser
    raises a SystemExit exception.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-h"])
        parse_args()

# version


def test_version(monkeypatch):
    """
    Test the version option.

    This test ensures that when the -v option is provided, the parser
    raises a SystemExit exception.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-v"])
        parse_args()


# debug

def test_debug(monkeypatch):
    """
    Test the debug option.

    This test ensures that when the -d option is provided, the parser
    correctly sets the debug flag to True in the configuration.
    """

    monkeypatch.setattr(sys, 'argv', ["othello", "-d"])
    mode, parseConfig = parse_args()

    assert parseConfig["debug"] is True

# size


def test_size(monkeypatch):
    """
    Test the size option.

    This test ensures that when the -s option is provided with a valid size,
    the parser correctly sets the size in the configuration.
    """

    monkeypatch.setattr(sys, 'argv', ["othello", "-s", "10"])
    mode, parseConfig = parse_args()

    assert parseConfig["size"] == 10


# TEST MODES

# blitz mode
def test_blitzMode(monkeypatch):
    """
    Test the blitz mode option.

    This test ensures that when the -b option is provided, the parser
    correctly sets the game mode to Blitz and sets the time limit to 30
    seconds. Also, when the -t option is provided after -b, the parser
    correctly sets the time limit to the specified value.
    """
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
    """
    Test the contest mode option.

    This test ensures that when the -c option is provided with a valid filename,
    the parser correctly sets the game mode to Contest and sets the filename
    in the configuration.
    """
    monkeypatch.setattr(sys, 'argv', ["othello", "-c", "dummyGame.txt"])
    mode, parseConfig = parse_args()

    assert mode == GameMode.CONTEST
    assert parseConfig["cFile"] == "dummyGame.txt"

# ai


def test_aiMode(monkeypatch):
    """
    Test the AI mode option.

    This test ensures that when the -a option is provided with a valid color,
    the parser correctly sets the game mode to AI and sets the color in the
    configuration.
    """
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
    """
    Test the error handling of the parser for invalid options.

    This test ensures that when an invalid option is provided, the parser raises
    a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "--invalid"])
        parse_args()


# mode incompatibility
def test_errIncompModes(monkeypatch):
    """
    Test the error handling of the parser for incompatible game modes.

    This test ensures that when game modes are provided that cannot be used
    together, the parser raises a SystemExit exception with a non-zero exit
    status.
    """
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
    """
    Test the error handling of the parser for invalid board sizes.

    This test ensures that when the user provides a board size that is not
    supported, the parser raises a SystemExit exception with a non-zero exit
    status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-s", "3"])
        parse_args()


# incorrect blitz time
def test_errTime(monkeypatch):  # trouver le moyen de faire plusieurs tests
    """
    Test the error handling of the parser for invalid blitz time values.

    This test ensures that when a negative or zero time value is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-b", "-t", "-20"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-t", "20"])
        parse_args()

# incorrect contest file


def test_errContest(monkeypatch):
    """
    Test the error handling of the parser for invalid contest mode arguments.

    This test ensures that when the contest mode is specified without a
    filename, the parser raises a SystemExit exception with a non-zero exit
    status.
    """

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-c"])
        parse_args()

    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-c", ""])
        parse_args()

# incorrect ai color


def test_errColor(monkeypatch):
    """
    Test the error handling of the parser for invalid AI color arguments.

    This test ensures that when an invalid AI color is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-aB"])
        parse_args()

# incorrect ai color


def test_errAI(monkeypatch):
    """
    Test the error handling of the parser for invalid AI arguments.

    This test ensures that when an invalid AI argument is provided, the parser
    raises a SystemExit exception with a non-zero exit status.
    """
    with pytest.raises(SystemExit):
        monkeypatch.setattr(sys, 'argv', ["othello", "-a[invalid]"])
        parse_args()
