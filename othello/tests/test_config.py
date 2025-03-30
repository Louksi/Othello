import pytest
import os
import sys
from io import StringIO

from othello.config import save_config, load_config, display_config


@pytest.fixture
def temp_config_file(tmpdir):
    """
    Creates a temporary file used to test saving and loading of configuration
    files. The file is deleted after the test is run.

    Yields:
        str: The path to the temporary file.
    """
    temp_file = tmpdir.join("test_config.othellorc")
    yield str(temp_file)
    if os.path.exists(temp_file):
        os.remove(temp_file)


def test_save_and_load_config(temp_config_file):
    # Define a sample configuration
    sample_config = {
        "mode": "normal",
        "filename": "save.feur",
        "size": "8",
        "debug": "false",
        "blitz_time": "30",
        "ai_color": "X",
        "ai_mode": "minimax",
        "ai_shallow": "true",
        "ai_depth": "3",
        "ai_heuristic": "default",
        "ai_time": "5",
    }

    save_config(
        sample_config, filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    loaded_config = load_config(
        filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    assert loaded_config == sample_config


def test_load_nonexistent_config():
    with pytest.raises(FileNotFoundError):
        load_config(filename_prefix="nonexistent")


def test_save_config_invalid_filename():
    invalid_config = {"mode": "normal"}
    with pytest.raises(IOError):
        save_config(invalid_config, filename_prefix="/invalid/path/test_config")


def test_load_config_invalid_filename():
    with pytest.raises(FileNotFoundError):
        load_config(filename_prefix="/invalid/path/test_config")


def test_save_and_load_empty_config(temp_config_file):
    empty_config = {}

    save_config(
        empty_config, filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    loaded_config = load_config(
        filename_prefix=temp_config_file.replace(".othellorc", "")
    )

    assert loaded_config == empty_config


def test_display_config():
    """
    Test display_config with an empty dictionnary, and one containing a small configuration
    """
    dummy_config = {}
    expected_output = "Configuration:\n"
    captured_output = StringIO()

    # redirect stdout into our variable, then reset it
    sys.stdout = captured_output
    display_config(dummy_config)
    sys.stdout = sys.__stdout__

    assert expected_output == captured_output.getvalue()

    dummy_config2 = {"mode": "normal", "filename": None, "size": 8}
    expected_output2 = "Configuration:\n  mode: normal\n  filename: None\n  size: 8\n"
    captured_output2 = StringIO()

    sys.stdout = captured_output2
    display_config(dummy_config2)
    sys.stdout = sys.__stdout__

    assert expected_output2 == captured_output2.getvalue()


def test_invalid_display_config():
    invalid_config = ["not a dict"]
    invalid_config2 = "not_a_dict"
    invalid_config3 = 299.792

    with pytest.raises(SystemExit):
        display_config(invalid_config)
    with pytest.raises(SystemExit):
        display_config(invalid_config2)
    with pytest.raises(SystemExit):
        display_config(invalid_config3)
