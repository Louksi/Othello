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

# from othello.parser import parse_args, default_config
from othello.othello_board import OthelloBoard


def save_config(config, filename_prefix="default"):
    """
    Save configuration into a .othellorc file, .ini format
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


def load_config(filename_prefix="default") -> dict:
    """
    Loading a configuration from a .othellorc file

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


def save_board_state_history(board: OthelloBoard, filename_prefix="default"):
    """
    Save the board state history into a .othellorc file.

    Args:
        board (OthelloBoard): The Othello board object containing the game state.
        filename_prefix (str): Prefix for the filename.
    """
    filename = f"{filename_prefix}.othellorc"
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(board.export())  # Write the board state as a string
    except IOError as err:
        print(f"Error while saving board state: {err}")
        raise


# def main():

#     mode, config = parse_args()

#     current_config = default_config.copy()
#     current_config.update(config)

#     # Converts all bool values into str
#     for key in current_config:
#         if isinstance(current_config[key], bool):
#             current_config[key] = str(current_config[key]).lower()

#     filename_prefix = "config"

#     save_config(current_config, filename_prefix)

#     loaded_config = load_config(filename_prefix)
#     print("Config loaded:", loaded_config)


# if __name__ == "__main__":
#     main()
