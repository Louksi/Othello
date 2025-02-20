import pytest
import os
from othello.config import save_config, load_config


@pytest.fixture
def temp_config_file(tmpdir):
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
        "ai_time": "5"
    }

    save_config(sample_config,
                filename_prefix=temp_config_file.replace(".othellorc", ""))

    loaded_config = load_config(
        filename_prefix=temp_config_file.replace(".othellorc", ""))

    assert loaded_config == sample_config


def test_load_nonexistent_config():
    with pytest.raises(FileNotFoundError):
        load_config(filename_prefix="nonexistent")


def test_save_config_invalid_filename():
    invalid_config = {"mode": "normal"}
    with pytest.raises(IOError):
        save_config(invalid_config,
                    filename_prefix="/invalid/path/test_config")


def test_load_config_invalid_filename():
    with pytest.raises(Exception):
        load_config(filename_prefix="/invalid/path/test_config")


def test_save_and_load_empty_config(temp_config_file):
    empty_config = {}

    save_config(
        empty_config, filename_prefix=temp_config_file.replace(".othellorc", ""))

    loaded_config = load_config(
        filename_prefix=temp_config_file.replace(".othellorc", ""))

    assert loaded_config == empty_config
