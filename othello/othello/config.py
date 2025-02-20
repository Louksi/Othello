# CONFIG FILE
# mode = normal/blitz/contest/ai
# filename = save.feur/None
# size = 6/8/10/12
# debug = false/true
# blitz_time = 30/X (en minutes)
# ai_color = X/O/A
# ai_mode = minimax/alphabeta
# ai_shallow = true/false
# ai_depth = 3/X (sachant que root_depth = 0)
# ai_heuristic = default/autre
# ai_time = 5/X (en secondes)


from othello.parser import parse_args, default_config


def save_config(config, filename_prefix="default"):
    """
    Save configuration into a .othellorc file, .ini format
    """
    filename = f"{filename_prefix}.othellorc"
    try:
        with open(filename, "w") as f:
            for key, value in config.items():
                f.write(f"{key}={value}\n")
    except IOError as e:
        print(f"Error while saving configuration: {e}")
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
        with open(filename, "r") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    config[key] = value
    except FileNotFoundError:
        print("No config file found, will take default configuration.")
        raise
    return config


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
