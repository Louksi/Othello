from gi.repository import Gtk, Gdk, GLib
import cairo
import gi

from othello.othello_board import Color, OthelloBoard
gi.require_version("Gtk", "4.0")


class OthelloGUI(Gtk.Application):
    def __init__(self, board: OthelloBoard):
        super().__init__(application_id="othello")
        GLib.set_application_name("othello")
        self.grid_size = board.size.value
        self.cell_size = 50
        self.board = board
        self.initialize_ui_components()

    def initialize_ui_components(self):
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_content_width(self.grid_size * self.cell_size)
        self.drawing_area.set_content_height(self.grid_size * self.cell_size)

        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.board_click)
        self.drawing_area.add_controller(click_gesture)

        self.black_timer_label = Gtk.Label(label="Black: 12:00")
        self.white_timer_label = Gtk.Label(label="White: 12:00")
        self.plays_list = Gtk.ListBox()
        self.black_last_move = Gtk.Label(label="Black last move: --:--")
        self.white_last_move = Gtk.Label(label="White last move: --:--")

    def update_game_state(self, x: int, y: int):
        print(f"Updating game state for move at {x}, {y}")
        self.drawing_area.queue_draw()
        self.board.play(x, y)
        print(self.board.export())

    def update_timers(self):
        self.black_timer_label.set_text("Black: 11:59")
        self.white_timer_label.set_text("White: 11:58")

    def update_play_history(self, x: int, y: int):
        new_move = Gtk.Label(label=f"Move to {chr(ord('A') + x)}{y + 1}")
        self.plays_list.prepend(new_move)
        if len(self.plays_list) > 5:
            self.plays_list.remove(self.plays_list.get_last_child())

    def update_last_moves(self, x: int, y: int):
        self.black_last_move.set_text(
            f"Black last move: {chr(ord('A') + x)}{y + 1}")

    def board_click(self, a, b, click_x: float, click_y: float):
        board_x = int(click_x / self.cell_size)
        board_y = int(click_y / self.cell_size)
        if 0 <= board_x < self.grid_size and 0 <= board_y < self.grid_size:
            self.update_game_state(board_x, board_y)

    def draw(self, area: Gtk.DrawingArea, cr: cairo.Context, width: int, height: int):
        self.draw_board(cr)
        self.draw_grid(cr)
        self.draw_pieces(cr)
        self.draw_line_cap_move(cr)

    def draw_board(self, cr: cairo.Context):
        BOARD_COLOR = (0.2, 0.6, 0.2)
        cr.set_source_rgb(*BOARD_COLOR)
        cr.paint()

    def draw_grid(self, cr: cairo.Context):
        GRID_COLOR = (0.1, 0.4, 0.1)
        cr.set_line_width(1)
        cr.set_source_rgb(*GRID_COLOR)

        for x in range(self.grid_size + 1):
            cr.move_to(x * self.cell_size, 0)
            cr.line_to(x * self.cell_size, self.grid_size * self.cell_size)

        for y in range(self.grid_size + 1):
            cr.move_to(0, y * self.cell_size)
            cr.line_to(self.grid_size * self.cell_size, y * self.cell_size)

        cr.stroke()

    def draw_line_cap_move(self, cr: cairo.Context):
        BLACK_PIECE_COLOR = (0, 0, 0, .3)
        WHITE_PIECE_COLOR = (1, 1, 1, .3)
        legal_moves = self.board.line_cap_move(self.board.current_player)
        print(legal_moves)
        for x in range(self.grid_size):
            for y in range(self.grid_size):
                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                radius = self.cell_size // 2 - 2
                if legal_moves.get(x, y):
                    color = BLACK_PIECE_COLOR if self.board.current_player == Color.BLACK else WHITE_PIECE_COLOR
                    cr.set_source_rgba(*color)
                    cr.arc(center_x, center_y, radius, 0, 2*3.14159)
                    cr.fill()

    def draw_pieces(self, cr: cairo.Context):
        BLACK_PIECE_COLOR = (0, 0, 0)
        WHITE_PIECE_COLOR = (1, 1, 1)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                radius = self.cell_size // 2 - 2

                if self.board.black.get(x, y):
                    cr.set_source_rgb(*BLACK_PIECE_COLOR)
                elif self.board.white.get(x, y):
                    cr.set_source_rgb(*WHITE_PIECE_COLOR)
                else:
                    continue

                cr.arc(center_x, center_y, radius, 0, 2 * 3.14159)
                cr.fill()

    def do_activate(self):
        win = Gtk.ApplicationWindow(application=self, title="Othello")
        win.set_default_size(800, 600)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        win.set_child(main_box)

        main_grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        main_box.append(main_grid)

        timer_box = Gtk.Box(spacing=10)
        timer_box.append(self.black_timer_label)
        timer_box.append(self.white_timer_label)
        main_grid.attach(timer_box, 0, 0, 1, 1)

        main_grid.attach(Gtk.Label(label=""), 1, 0, 1, 1)

        board_container = Gtk.Grid(column_spacing=0, row_spacing=0)
        main_grid.attach(board_container, 0, 1, 1, 1)

        col_labels_grid = Gtk.Grid(column_homogeneous=True)
        col_labels_grid.set_size_request(self.grid_size * self.cell_size, 20)
        for col in range(self.grid_size):
            label_text = chr(ord('A') + col)
            label = Gtk.Label(label=label_text)
            label.set_halign(Gtk.Align.CENTER)
            col_labels_grid.attach(label, col, 0, 1, 1)
        board_container.attach(col_labels_grid, 1, 0, 1, 1)

        row_labels_grid = Gtk.Grid(row_homogeneous=True)
        row_labels_grid.set_size_request(20, self.grid_size * self.cell_size)
        for row in range(self.grid_size):
            label_text = str(row + 1)
            label = Gtk.Label(label=label_text)
            label.set_valign(Gtk.Align.CENTER)
            row_labels_grid.attach(label, 0, row, 1, 1)
        board_container.attach(row_labels_grid, 0, 1, 1, 1)

        board_container.attach(self.drawing_area, 1, 1, 1, 1)

        plays_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        plays_label = Gtk.Label(label="Last 5 Plays")
        plays_box.append(plays_label)

        for i in range(5):
            self.plays_list.append(Gtk.Label(label=f"Play {i+1}"))
        plays_box.append(self.plays_list)

        main_grid.attach(plays_box, 1, 1, 1, 1)

        buttons_grid = Gtk.Grid(row_spacing=5, column_spacing=5)
        button1 = Gtk.Button(label="Button 1")
        button2 = Gtk.Button(label="Button 2")
        button3 = Gtk.Button(label="Button 3")
        button4 = Gtk.Button(label="Button 4")
        buttons_grid.attach(button1, 0, 0, 1, 1)
        buttons_grid.attach(button2, 1, 0, 1, 1)
        buttons_grid.attach(button3, 0, 1, 1, 1)
        buttons_grid.attach(button4, 1, 1, 1, 1)

        main_grid.attach(buttons_grid, 0, 2, 1, 1)

        last_moves_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5)
        last_moves_box.append(self.black_last_move)
        last_moves_box.append(self.white_last_move)

        main_grid.attach(last_moves_box, 1, 2, 1, 1)

        win.present()
