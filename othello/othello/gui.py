from othello.blitz_timer import BlitzTimer
from othello.othello_board import Color, GameOverException, OthelloBoard
import othello.logger as log
from gi.repository import Gtk, GLib, Adw
import time
import threading
import cairo
import gi
import math
import logging
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

logger = logging.getLogger("Othello")


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


class OthelloGUI(Gtk.Application):
    PLAYS_IN_HISTORY = 15

    def __init__(self, board: OthelloBoard, time_limit: int | None = None):
        logger.debug(
            "Graphic User Interface is in use. Entering GUI initialization function from gui.py.")
        super().__init__(application_id="othello")
        GLib.set_application_name("othello")
        self.board = board
        self.time_limit = time_limit
        logger.debug(f"   Game initialized with board:\n{self.board}.")

    def do_activate(self):
        logger.debug("Entering do_activate function from gui.py.")
        window = OthelloWindow(self, self.board, self.time_limit)
        window.present()


class OthelloWindow(Gtk.ApplicationWindow):
    def __init__(self, application, board: OthelloBoard, time_limit: int | None = None):
        logger.debug(
            "Entering initialization function for game window from gui.py.")
        super().__init__(application=application, title="Othello")
        self.set_default_size(800, 600)
        self.over = False
        self.over_message = None
        self.__init(board, time_limit)

    def __init(self, board, time_limit):
        logger.debug(
            "Entering initialization function for game window from gui.py.")
        self.board = board
        self.blitz_timer: None | BlitzTimer = None
        self.is_blitz = time_limit is not None
        if self.is_blitz:
            self.blitz_timer = BlitzTimer(time_limit)
            self.time_limit = time_limit
        self.grid_size = board.size.value
        self.cell_size = 50

        self.initialize_ui_components()
        self.create_layout()
        self.connect_signals()
        if self.blitz_timer is not None:
            self.blitz_timer.start_timer("black")
            self.blitz_loser = None

    def initialize_ui_components(self):
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_content_width(self.grid_size * self.cell_size)
        self.drawing_area.set_content_height(self.grid_size * self.cell_size)

        if self.is_blitz:
            self.black_timer_label = Gtk.Label()
            self.white_timer_label = Gtk.Label()
            self.blitz_thread = threading.Thread(
                target=self.update_timers_thread)
            self.blitz_thread.daemon = True
            self.blitz_thread.start()
        self.plays_list = ListBoxWithLength()
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

        if self.is_blitz:
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
        plays_box.append(
            Gtk.Label(label=f"Last {OthelloGUI.PLAYS_IN_HISTORY} Plays"))
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
        # last_moves_box.append(self.black_last_move)
        # last_moves_box.append(self.white_last_move)
        main_grid.attach(last_moves_box, 1, 3, 1, 1)

    # Game state management methods
    def update_game_state(self):
        if self.over:
            self.show_error_dialog(self.over_message)
        self.drawing_area.queue_draw()
        self.update_nb_pieces()

    def update_nb_pieces(self):
        self.black_nb_pieces.set_label(
            f"Black has {self.board.black.popcount()} pieces")
        self.white_nb_pieces.set_label(
            f"White has {self.board.white.popcount()} pieces")

    def update_timers_thread(self):
        if self.blitz_timer is not None:
            while not self.over:
                GLib.idle_add(self.update_timers)
                if self.blitz_timer.is_time_up("black" if self.board.current_player is Color.BLACK else "white"):
                    self.blitz_loser = self.board.current_player
                    GLib.idle_add(self.update_game_state)
                    self.over = True
                    self.over_message = f"{self.blitz_loser} lost due to time"
                time.sleep(1)

    def update_timers(self):
        self.black_timer_label.set_text(
            f"Black: {self.blitz_timer.display_time_player(Color.BLACK)}")
        self.white_timer_label.set_text(
            f"White: {self.blitz_timer.display_time_player(Color.WHITE)}")

    def update_play_history(self, x: int, y: int):
        new_move = Gtk.Label(
            label=f"{self.board.get_last_play()[4]} placed a piece at {chr(ord('A') + x)}{y + 1}")
        self.plays_list.prepend(new_move)
        if len(self.plays_list) > OthelloGUI.PLAYS_IN_HISTORY:
            self.plays_list.remove(self.plays_list.get_last_child())

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
                    cr.arc(center_x, center_y, radius, 0, 2*math.pi)
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

    def board_click(self, _gesture, _n_press, click_x: float, click_y: float):
        if self.over:
            return
        board_x = int(click_x / self.cell_size)
        board_y = int(click_y / self.cell_size)
        if 0 <= board_x < self.grid_size and 0 <= board_y < self.grid_size:
            try:
                self.board.play(board_x, board_y)
                self.update_play_history(board_x, board_y)
                if self.blitz_timer is not None:
                    self.blitz_timer.change_player(
                        "black" if self.board.current_player is Color.BLACK else "white")
            except GameOverException as err:
                self.over_message = err
                self.over = True
            self.update_game_state()

    def forfeit_handler(self, _button: Gtk.Button):
        self.show_confirm_dialog(
            "are you sure ? this will close the program and your progression will be lost!", self.forfeit_handler_callback)

    def forfeit_handler_callback(self, response):
        if response == -5:
            exit(0)  # todo: maybe be a little more subtle

    def restart_handler(self, _button: Gtk.Button):
        self.show_confirm_dialog(
            "Are you sure you want to restart the game ?", self.restart_handler_callback)

    def restart_handler_callback(self, confirmation):
        if confirmation == -5:
            self.over = True
            self.blitz_thread.join()
            self.board.restart()
            for _ in range(len(self.plays_list)):
                self.plays_list.remove(self.plays_list.get_last_child())
            self.update_nb_pieces()
            self.over = False
            self.__init(self.board, self.time_limit)

    def file_chooser(self, callback, default_file_name: str, file_extension: str):
        dialog = Gtk.FileChooserDialog(
            title="Save Game",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.ACCEPT)
        dialog.set_modal(True)
        dialog.set_current_name(f"{default_file_name}.{file_extension}")
        filter_sav = Gtk.FileFilter()
        filter_sav.set_name("Othello Save Files")
        filter_sav.add_pattern(f"*.{file_extension}")
        dialog.add_filter(filter_sav)
        filter_all = Gtk.FileFilter()
        filter_all.set_name("All Files")
        filter_all.add_pattern("*")
        dialog.add_filter(filter_all)
        dialog.connect("response", callback)
        dialog.present()

    def save_and_quit_handler(self, _button: Gtk.Button):
        self.file_chooser(self.on_save_dialog_response, "my_game", ".sav")

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

    def save_history_handler(self, _button: Gtk.Button):
        self.file_chooser(self.save_history_handler_callback,
                          "my_hist", ".hist")

    def save_history_handler_callback(self, file_path):
        try:
            with open(file_path, "w") as file:
                game_data = self.board.export_history()
                file.write(game_data)
            print(f"Game saved to {file_path}")
        except Exception as e:
            self.show_error_dialog(f"Failed to save game history: {str(e)}")

    def show_confirm_dialog(self, message, cb):
        def call_cb(d, r):
            d.destroy()
            cb(r)

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=message
        )
        dialog.connect("response", call_cb)
        dialog.present()

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
