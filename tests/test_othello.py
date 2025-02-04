"""Dummy test case for the moment"""

import pytest
from othello.othello import main

def test_main(capfd):
    """Test the hello world from main"""
    main()
    out, err = capfd.readouterr()
    assert out == "Hello, World!\n"
    assert err == ""
