'''
        CONFIG FILE
mode = normal/blitz/contest/ai
filename = save.feur/None
size = 6/8/10/12
debug = false/true
blitz_time = 30/X (en minutes)
ai_color = X/O/A
ai_mode = minimax/alphabeta
ai_shallow = true/false
ai_depth = 3/X (sachant que root_depth = 0)
ai_heuristic = default/autre
ai_time = 5/X (en secondes)
'''

import sys


def save_config(config: dict, filename_prefix: str = "current_config") -> None:
    """
    Save configuration into a .othellorc file, .ini format.

    Arguments:
      config (dict): The configuration to save
      filename_prefix (str): The prefix for the filename (default: "current_config")
    """

    filename = f"{filename_prefix}.othellorc"
    try:
        # converts all boolean values into str
        for key in config:
            if isinstance(config[key], bool):
                config[key] = str(config[key]).lower()

        with open(filename, "w", encoding="utf-8") as file:
            for key, value in config.items():
                file.write(f"{key}={value}\n")
    except IOError as err:
        print(f"Error while saving configuration: {err}")
        raise


def load_config(filename_prefix: str = "current_config") -> dict:
    """
    Loading a configuration from a .othellorc file.

    Argument:
      filename_prefix (str): The prefix for the filename (default: "current_config")

    Returns:
      dict: Dictionnary containing the configuration from the file
    """
    filename = f"{filename_prefix}.othellorc"
    config = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    except FileNotFoundError:
        print("No config file found, will take default configuration.")
        raise
    return config


def display_config(config: dict) -> None:
    """
    Display the configuration.

    Argument:
      config (dict): The configuration to display

    Raises:
      SystemExit: if invalid arguments are provided
    """
    if not isinstance(config, dict):
        sys.stderr.write("Error: expected a dictionnary.\n\n")
        sys.exit(1)

    print("Configuration:")
    for key, value in config.items():
        print(f"  {key}: {value}")
