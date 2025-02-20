import sys
import othello.othello_board as board
from othello.othello_board import OthelloBoard, BoardSize, Color

class NormalMode:
    def __init__(self,  board_size: BoardSize = BoardSize.EIGHT_BY_EIGHT):
            self.board_size = BoardSize(board_size) if isinstance(board_size, int) else board_size
            self.board = OthelloBoard(self.board_size)
            self.current_player = Color.BLACK

    def print_board(self):
        print(str(self.board))

    def print_possible_moves(self,possible_moves, size):
        print("Possible moves:")
        for y in range(size):
            for x in range(size):
                if possible_moves.get(x, y):
                    print(f"{chr(ord('a')+x)}{y+1}", end=" ")
        print()

    def get_valid_move(self, possible_moves, size):
        while True:
            move = input("Enter your move: ").strip().lower()
            
            if len(move) < 2 or move[0] not in "abcdef"[:size] or not move[1:].isdigit():
                print("Invalid move format. Try again.")
                continue
            
            x_coord = ord(move[0]) - ord('a')
            y_coord = int(move[1]) - 1
            
            if not possible_moves.get(x_coord, y_coord):
                print("Invalid move. Not a legal play. Try again.")
                continue
            
            return x_coord, y_coord

    def switch_player(self, current_player):
        return board.Color.WHITE if current_player == board.Color.BLACK else board.Color.BLACK


    def is_game_over(self, current_player):
        possible_moves_black = self.board.line_cap_move(board.Color.BLACK)
        possible_moves_white = self.board.line_cap_move(board.Color.WHITE)

        no_black = possible_moves_black.bits == 0
        no_white = possible_moves_white.bits == 0

        if no_black and no_white:
            print("No valid moves for both players. Game over.")
            return True 

        if current_player == board.Color.BLACK and no_black:
            print("Black has no valid moves. Skipping turn...")
            return "skip" 

        if current_player == board.Color.WHITE and no_white:
            print("White has no valid moves. Skipping turn...")
            return "skip" 

        return False 
    
    def normal_moves(self):
        return self.board.line_cap_move(self.current_player)
    
    def play(self, x_coord: int, y_coord: int):
        self.board.play(x_coord, y_coord)
def normal_play(size):
    b = NormalMode(size)
    current_player = board.Color.BLACK

    while True:
        no_black, no_white = False, False
        
        b.print_board()
        print(f"\n{current_player.name}'s turn ({current_player.value})")
        
        possible_moves = b.normal_moves()

        if b.is_game_over(current_player):
            break

        
        b.print_possible_moves(possible_moves, b.board.size.value)
        
        x_coord, y_coord = b.get_valid_move(possible_moves, b.board.size.value)
        b.play(x_coord, y_coord)
        
        current_player = b.switch_player(current_player)
