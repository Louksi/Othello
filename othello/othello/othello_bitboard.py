from othello.othello_player import PlayerColor


class BoardSizeException(Exception):
    def __init__(self, given_size: int):
        self.message = f"Board size should be a multiple of 2, currently {given_size}"


class OthelloBitboard:
    def __init__(self, size: int):
        if size & 1 != 0:
            raise BoardSizeException(size)

        self.size = size
        self.current_player = PlayerColor.BLACK

        self.board_mask = 0
        self.black = 0
        for i in range(size*size):
            self.board_mask |= 1 << i
