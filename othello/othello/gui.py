from othello.othello_board import Color, GameOverException, OthelloBoard
from gi.repository import Gtk, GLib, Adw
import cairo
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


class ListBoxWithLength(Gtk.ListBox):
    def __init__(self):
        super().__init__()
        self.length = 0

    def prepend(self, child: Gtk.Widget) -> None:
        super().prepend(child)
        self.length += 1

    def append(self, child: Gtk.Widget) -> None:
        super().append(child)
        self.length += 1

    def remove(self, child: Gtk.Widget) -> None:
        super().remove(child)
        self.length -= 1

    def __len__(self) -> int:
        return self.length


class OthelloWindow(Gtk.ApplicationWindow):
    def __init__(self, application, board: OthelloBoard):
        super().__init__(application=application, title="Othello")
        self.set_default_size(800, 600)

        self.board = board
        self.grid_size = board.size.value
        self.cell_size = 50

        self.initialize_ui_components()
        self.create_layout()
        self.connect_signals()

    def initialize_ui_components(self):
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_content_width(self.grid_size * self.cell_size)
        self.drawing_area.set_content_height(self.grid_size * self.cell_size)

        self.black_timer_label = Gtk.Label(label="Black: 12:00")
        self.white_timer_label = Gtk.Label(label="White: 12:00")
        self.plays_list = ListBoxWithLength()
        self.black_last_move = Gtk.Label(label="Black last move: --:--")
        self.white_last_move = Gtk.Label(label="White last move: --:--")
        self.black_nb_pieces = Gtk.Label(label="Black has 2 pieces")
        self.white_nb_pieces = Gtk.Label(label="White has 2 pieces")

        self.forfeit_button = Gtk.Button(label="forfeit")
        self.save_quit_button = Gtk.Button(label="save and quit")
        self.restart_button = Gtk.Button(label="restart")
        self.save_history_button = Gtk.Button(label="save history")

    def connect_signals(self):
        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.board_click)
        self.drawing_area.add_controller(click_gesture)
        self.forfeit_button.connect("clicked", self.forfeit_handler)
        self.save_quit_button.connect("clicked", self.save_and_quit_handler)
        self.restart_button.connect("clicked", self.restart_handler)
        self.save_history_button.connect("clicked", self.save_history_handler)

    def create_layout(self):
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        self.set_child(main_box)

        main_grid = Gtk.Grid(column_spacing=20, row_spacing=20)
        main_box.append(main_grid)

        timer_box = Gtk.Box(spacing=10)
        timer_box.append(self.black_timer_label)
        timer_box.append(self.white_timer_label)
        main_grid.attach(timer_box, 0, 0, 1, 1)
        main_grid.attach(Gtk.Label(label=""), 1, 0, 1, 1)

        board_container = Gtk.Grid()
        main_grid.attach(board_container, 0, 1, 1, 1)
        col_labels_grid = Gtk.Grid(column_homogeneous=True)
        col_labels_grid.set_size_request(self.grid_size * self.cell_size, 20)
        for col in range(self.grid_size):
            label = Gtk.Label(label=chr(ord('A') + col))
            label.set_halign(Gtk.Align.CENTER)
            col_labels_grid.attach(label, col, 0, 1, 1)
        board_container.attach(col_labels_grid, 1, 0, 1, 1)

        row_labels_grid = Gtk.Grid(row_homogeneous=True)
        row_labels_grid.set_size_request(20, self.grid_size * self.cell_size)
        for row in range(self.grid_size):
            label = Gtk.Label(label=str(row + 1))
            label.set_valign(Gtk.Align.CENTER)
            row_labels_grid.attach(label, 0, row, 1, 1)
        board_container.attach(row_labels_grid, 0, 1, 1, 1)

        board_container.attach(self.drawing_area, 1, 1, 1, 1)

        nb_pieces_box = Gtk.Box(spacing=10)
        nb_pieces_box.append(self.black_nb_pieces)
        nb_pieces_box.append(self.white_nb_pieces)
        main_grid.attach(nb_pieces_box, 0, 2, 1, 1)

        plays_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        plays_box.append(Gtk.Label(label="Last 5 Plays"))
        plays_box.append(self.plays_list)
        main_grid.attach(plays_box, 1, 1, 1, 1)

        buttons_grid = Gtk.Grid(row_spacing=5, column_spacing=5)
        buttons_grid.attach(self.forfeit_button, 0, 0, 1, 1)
        buttons_grid.attach(self.save_quit_button, 1, 0, 1, 1)
        buttons_grid.attach(self.restart_button, 0, 1, 1, 1)
        buttons_grid.attach(self.save_history_button, 1, 1, 1, 1)
        main_grid.attach(buttons_grid, 0, 3, 1, 1)

        last_moves_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=5)
        last_moves_box.append(self.black_last_move)
        last_moves_box.append(self.white_last_move)
        main_grid.attach(last_moves_box, 1, 3, 1, 1)

    def update_game_state(self, x: int, y: int):
        try:
            self.board.play(x, y)
        except GameOverException as err:
            self.show_error_dialog(err)
        self.drawing_area.queue_draw()
        self.black_nb_pieces.set_label(
            f"Black has {self.board.black.popcount()} pieces")
        self.white_nb_pieces.set_label(
            f"White has {self.board.white.popcount()} pieces")
        self.update_play_history(x, y)

    def update_timers(self):
        self.black_timer_label.set_text("Black: 11:59")
        self.white_timer_label.set_text("White: 11:58")

    def update_play_history(self, x: int, y: int):
        new_move = Gtk.Label(
            label=f"{self.board.get_last_play()[4]} placed a piece at {chr(ord('A') + x)}{y + 1}")
        self.plays_list.prepend(new_move)
        if len(self.plays_list) > 5:
            self.plays_list.remove(self.plays_list.get_last_child())

    def update_last_moves(self, x: int, y: int):
        self.black_last_move.set_text(
            f"Black last move: {chr(ord('A') + x)}{y + 1}")

    def board_click(self, _gesture, _n_press, click_x: float, click_y: float):
        board_x = int(click_x / self.cell_size)
        board_y = int(click_y / self.cell_size)
        if 0 <= board_x < self.grid_size and 0 <= board_y < self.grid_size:
            self.update_game_state(board_x, board_y)

    def draw(self, _area: Gtk.DrawingArea, cr: cairo.Context, width: int, height: int):
        self.draw_board(cr)
        self.draw_grid(cr)
        self.draw_pieces(cr)
        self.draw_legal_moves(cr)

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

    def draw_legal_moves(self, cr: cairo.Context):
        BLACK_PIECE_COLOR = (0, 0, 0, .3)
        WHITE_PIECE_COLOR = (1, 1, 1, .3)
        legal_moves = self.board.line_cap_move(self.board.current_player)

        color = BLACK_PIECE_COLOR if self.board.current_player == Color.BLACK else WHITE_PIECE_COLOR
        cr.set_source_rgba(*color)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if legal_moves.get(x, y):
                    center_x = x * self.cell_size + self.cell_size // 2
                    center_y = y * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 2 - 2
                    cr.arc(center_x, center_y, radius, 0, 2*3.14159)
                    cr.fill()

    def draw_pieces(self, cr: cairo.Context):
        BLACK_PIECE_COLOR = (0, 0, 0)
        WHITE_PIECE_COLOR = (1, 1, 1)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if not (self.board.black.get(x, y) or self.board.white.get(x, y)):
                    continue

                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                radius = self.cell_size // 2 - 2

                if self.board.black.get(x, y):
                    cr.set_source_rgb(*BLACK_PIECE_COLOR)
                else:
                    cr.set_source_rgb(*WHITE_PIECE_COLOR)

                cr.arc(center_x, center_y, radius, 0, 2 * 3.14159)
                cr.fill()

    def forfeit_handler(self, _button: Gtk.Button):
        print("clicked forfeit button")

    def save_and_quit_handler(self, _button: Gtk.Button):
        dialog = Gtk.FileChooserDialog(
            title="Save Game",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.ACCEPT)
        dialog.set_modal(True)
        dialog.set_current_name("othello_game.sav")
        filter_sav = Gtk.FileFilter()
        filter_sav.set_name("Othello Save Files")
        filter_sav.add_pattern("*.sav")
        dialog.add_filter(filter_sav)
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        dialog.connect("response", self.on_save_dialog_response)
        dialog.present()

    def on_save_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self.save_game_to_file(file_path)
            self.close()
        dialog.destroy()

    def save_game_to_file(self, file_path):
        try:
            with open(file_path, "w") as file:
                game_data = self.board.export()
                file.write(game_data)
            print(f"Game saved to {file_path}")
        except Exception as e:
            self.show_error_dialog(f"Failed to save game: {str(e)}")

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.connect("response", lambda d, _: d.destroy())
        dialog.present()

    def restart_handler(self, _button: Gtk.Button):
        print("clicked restart button")

    def save_history_handler(self, _button: Gtk.Button):
        print("clicked save history button")


class OthelloGUI(Gtk.Application):
    def __init__(self, board: OthelloBoard):
        super().__init__(application_id="othello")
        GLib.set_application_name("othello")
        self.board = board

    def do_activate(self):
        window = OthelloWindow(self, self.board)
        window.present()
