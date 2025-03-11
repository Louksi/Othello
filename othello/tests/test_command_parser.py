from othello.command_parser import CommandKind, CommandParser, CommandParserException, PlayCommand
import pytest


def test_help():
    cp = CommandParser(8)
    assert cp.parse_str("?") == (CommandKind.HELP,)


def test_rules():
    cp = CommandParser(8)
    assert cp.parse_str("r") == (CommandKind.RULES,)


def test_save():
    cp = CommandParser(8)
    assert cp.parse_str("s") == (CommandKind.SAVE_AND_QUIT,)


def test_save_hist():
    cp = CommandParser(8)
    assert cp.parse_str("sh") == (CommandKind.SAVE_HISTORY,)


def test_forfeit():
    cp = CommandParser(8)
    assert cp.parse_str("ff") == (CommandKind.FORFEIT,)


def test_restart():
    cp = CommandParser(8)
    assert cp.parse_str("restart") == (CommandKind.RESTART,)


def test_legal_plays():
    cp = CommandParser(8)
    assert cp.parse_str("b3") == (CommandKind.PLAY_MOVE, PlayCommand(1, 2))
    assert cp.parse_str("a4") == (CommandKind.PLAY_MOVE, PlayCommand(0, 3))
    assert cp.parse_str("a1") == (CommandKind.PLAY_MOVE, PlayCommand(0, 0))
    assert cp.parse_str("h8") == (CommandKind.PLAY_MOVE, PlayCommand(7, 7))


def test_illegal_plays():
    cp = CommandParser(6)
    with pytest.raises(CommandParserException):
        cp.parse_str("h8")
        cp.parse_str("a9")
        cp.parse_str("a0")


def test_illegal_data():
    cp = CommandParser(6)
    with pytest.raises(CommandParserException):
        cp.parse_str("aaaaaaaaaaaa")
