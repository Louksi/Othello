import othello.othello
from othello.othello_bitboard import OthelloBitboard, BoardSize, Color


def main():
    othello.othello.main()


if __name__ == "__main__":
    b = OthelloBitboard(BoardSize.EIGHT_BY_EIGHT)
    print(b.line_cap_move(Color.WHITE))
    print()
    cap = b.line_cap(4, 2, Color.WHITE)
    print(cap)
    print()
    b.white = b.white | cap
    b.black.bits = b.black.bits & ~(cap.bits)
    print(b)
