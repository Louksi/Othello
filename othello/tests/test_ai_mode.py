import pytest
import sys
from unittest.mock import MagicMock, patch, call
from othello.command_parser import CommandKind, CommandParser
from othello.othello.cli import NormalGame
from othello.othello_board import BoardSize, Color, Bitboard
