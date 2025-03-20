"""
CONFIG FILE

This module manages the configuration for the Othello game.

Configuration Options:
    - mode: normal/blitz/contest/ai
    - filename: save.feur/None
    - size: 6/8/10/12
    - debug: false/true
    - blitz_time: 30/X (minutes)
    - ai_color: X/O/A
    - ai_mode: minimax/alphabeta
    - ai_shallow: true/false
    - ai_depth: 3/X (root_depth = 0)
    - ai_heuristic: default/custom
    - ai_time: 5/X (seconds)
"""
# pylint: disable=locally-disabled, multiple-statements, line-too-long, import-error, no-name-in-module

import sys
import logging

from othello.othello_board import OthelloBoard
import othello.logger as log

logger = logging.getLogger("Othello")
SEPARATOR = "="


def save_config(config: dict, filename_prefix: str = "current_config") -> None:
    """Save configuration into a .othellorc file."""
    logger.debug("Saving configuration: %s with filename_prefix: %s",
                 config, filename_prefix)
    filename = f"{filename_prefix}.othellorc"

    try:
        file_content = "\n".join(
            f"{key}{SEPARATOR}{str(value).lower() if isinstance(value, bool) else value}"
            for key, value in config.items()
        )
    except Exception as err:
        logger.error("Failed to format configuration: %s", err)
        raise

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(file_content)
    except IOError as err:
        log.log_error_message(err, context="Error while saving configuration.")
        raise

    logger.debug(
        "Configuration saved successfully with %d entries.", len(config))


def load_config(filename_prefix: str = "current_config") -> dict:
    """Load a configuration from a .othellorc file."""
    logger.debug("Loading configuration with filename_prefix: %s",
                 filename_prefix)
    filename = f"{filename_prefix}.othellorc"
    config = {}

    try:
        with open(filename, "r", encoding="utf-8") as file:
            lines = file.readlines()
    except FileNotFoundError as err:
        log.log_error_message(err, context="No configuration file found.")
        raise

    try:
        for line in lines:
            if SEPARATOR in line:
                key, value = line.strip().split(SEPARATOR, 1)
                config[key] = value
    except ValueError as err:
        logger.error("Invalid configuration format: %s", err)
        raise

    return config


def save_board_state_history(board: OthelloBoard, filename_prefix="default") -> None:
    """Save the board state history into a .othellorc file."""
    logger.debug(
        "Saving board state history to filename_prefix: %s", filename_prefix)
    filename = f"{filename_prefix}.othellorc"

    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(board.export())
    except IOError as err:
        log.log_error_message(
            err, context=f"Failed to save board state to {filename}.")
        raise

    logger.debug("Board state successfully saved to %s", filename)


def display_config(config: dict) -> None:
    """Display the configuration."""
    logger.debug("Displaying configuration: %s", str(config))

    if not isinstance(config, dict):
        logger.error("Expected a dictionary.")
        sys.stderr.write("Error: Expected a dictionary.\n")
        sys.exit(1)

    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
