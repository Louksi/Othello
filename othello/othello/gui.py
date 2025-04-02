"""
Graphic interface to play the Othello game, inherits from __main__.py
"""

from gi import require_version

require_version("Gtk", "4.0")
require_version("Adw", "1")

from gi.repository import Gtk, GLib, Adw
from othello.controllers import GameController
import cairo
import time
import threading
import sys
import math
import logging
from othello.othello_board import (
    Color,
    GameOverException,
    IllegalMoveException,
    OthelloBoard,
)


logger = logging.getLogger("Othello")


class ListBoxWithLength(Gtk.ListBox):
    """
    A subclass of Gtk.ListBox that tracks its own length (number of children).
    This makes it easier to limit the history display to a fixed number of entries.
    """

    def __init__(self):
        """
        Initializes a ListBoxWithLength object.

        A ListBoxWithLength is a subclass of a Gtk.ListBox that has an additional
        `length` attribute, which is the number of children currently in the list
        box. This attribute is updated whenever items are added or removed from the
        list box.

        :return: A new ListBoxWithLength instance.
        :rtype: ListBoxWithLength
        """
        super().__init__()
        self.length = 0

    def prepend(self, child: Gtk.Widget, *args, **kwargs) -> None:
        """
        Prepends a child widget to the list box and increments the length attribute.

        :param child: The widget to prepend to the list box.
        :type child: Gtk.Widget
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().prepend(child, *args, **kwargs)
        self.length += 1

    def append(self, child: Gtk.Widget, *args, **kwargs) -> None:
        """
        Appends a child widget to the list box and increments the length attribute.

        :param child: The widget to append to the list box.
        :type child: Gtk.Widget
        :param args: Additional positional arguments.
        :param kwargs: Additional keyword arguments.
        """
        super().append(child, *args, **kwargs)
        self.length += 1

    def remove(self, child: Gtk.Widget) -> None:
        """
        Removes a child widget from the list box and decrements the length attribute.

        :param child: The widget to remove from the list box.
        :type child: Gtk.Widget
        """
        super().remove(child)
        self.length -= 1

    def __len__(self) -> int:
        """
        Returns the number of children currently in the list box.

        :return: The length of the list box.
        :rtype: int
        """
        return self.length


class OthelloGUI(Gtk.Application):
    """
    Main application class for the Othello GUI.
    Handles the application lifecycle and creates the main window.
    """

    PLAYS_IN_HISTORY = 15

    def __init__(self, board: GameController):
        """
        Initialize the Othello GUI application.

        :param board: The Othello game board
        :param time_limit: Optional time limit for blitz mode
        """
        logger.debug(
            "Graphic User Interface is in use. Entering GUI initialization function from gui.py."
        )
        super().__init__(application_id="fr.ubx.othello")
        GLib.set_application_name("othello")
        self.board = board
        logger.debug("Game initialized with board:\n%s", self.board)

    def do_activate(self):
        """
        Called when the application is activated.
        Creates and presents the main application window.
        """
        logger.debug("Entering do_activate function from gui.py.")
        window = OthelloWindow(self, self.board)
        window.present()


class OthelloWindow(Gtk.ApplicationWindow):
    """
    Main window for the Othello game.
    Contains the game board, controls, and displays game state.
    """

    def __init__(self, application, board: GameController):
        """
        Initialize the Othello game window.

        :param application: The parent application
        :param board: The Othello game board
        :param time_limit: Optional time limit for blitz mode
        """
        logger.debug("Entering initialization function for game window from gui.py.")
        super().__init__(application=application, title="Othello")
        self.quit = lambda: application.quit()
        self.set_default_size(800, 600)
        self.over = False
        self.over_message = None

        self.controller: GameController
        self.is_blitz = False
        self.grid_size = 0
        self.cell_size = 0
        self.drawing_area: Gtk.DrawingArea
        self.black_timer_label: Gtk.Label
        self.white_timer_label: Gtk.Label
        self.blitz_thread = None
        self.blitz_loser = None
        self.plays_list: ListBoxWithLength
        self.black_nb_pieces: Gtk.Label
        self.white_nb_pieces: Gtk.Label
        self.forfeit_button: Gtk.Button
        self.save_quit_button: Gtk.Button
        self.restart_button: Gtk.Button
        self.save_history_button: Gtk.Button

        self.logger = logging.getLogger("Othello")

        board.post_play_callback = self.update_game_state

        self.__init_game(board)

    def __init_game(self, board):
        """
        Initialize the game components and UI.

        :param board: The Othello game board
        :param time_limit: Optional time limit for blitz mode
        """
        logger.debug("Initializing game components and UI")
        self.controller = board
        self.is_blitz = self.controller.is_blitz
        self.grid_size = board.size.value
        self.cell_size = 50

        self.initialize_ui_components()
        self.create_layout()
        self.connect_signals()
        self.controller.next_move()

    def initialize_ui_components(self):
        """
        Initialize UI components like buttons, labels, and the drawing area.
        """
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_draw_func(self.draw)
        self.drawing_area.set_content_width(self.grid_size * self.cell_size)
        self.drawing_area.set_content_height(self.grid_size * self.cell_size)

        if self.is_blitz:
            self.black_timer_label = Gtk.Label()
            self.white_timer_label = Gtk.Label()
            self.blitz_thread = threading.Thread(target=self.update_timers_thread)
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
        """
        Connect UI elements to their event handlers.
        """
        click_gesture = Gtk.GestureClick.new()
        click_gesture.connect("pressed", self.board_click)
        self.drawing_area.add_controller(click_gesture)
        self.forfeit_button.connect("clicked", self.forfeit_handler)
        self.save_quit_button.connect("clicked", self.save_and_quit_handler)
        self.restart_button.connect("clicked", self.restart_handler)
        self.save_history_button.connect("clicked", self.save_history_handler)

    def create_layout(self):
        """
        Create and arrange the UI layout.
        """
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
            label = Gtk.Label(label=chr(ord("A") + col))
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
        plays_box.append(Gtk.Label(label=f"Last {OthelloGUI.PLAYS_IN_HISTORY} Plays"))
        plays_box.append(self.plays_list)
        main_grid.attach(plays_box, 1, 1, 1, 1)

        buttons_grid = Gtk.Grid(row_spacing=5, column_spacing=5)
        buttons_grid.attach(self.forfeit_button, 0, 0, 1, 1)
        buttons_grid.attach(self.save_quit_button, 1, 0, 1, 1)
        buttons_grid.attach(self.restart_button, 0, 1, 1, 1)
        buttons_grid.attach(self.save_history_button, 1, 1, 1, 1)
        main_grid.attach(buttons_grid, 0, 3, 1, 1)

        last_moves_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        main_grid.attach(last_moves_box, 1, 3, 1, 1)

    def update_game_state(self):
        """
        Update the game state after a move or game state change.
        Handles end-of-game conditions.
        """

        if self.controller.is_game_over:
            black_score = self.controller.popcount(Color.BLACK)
            white_score = self.controller.popcount(Color.WHITE)
            logger.debug("Final score - Black: %s, White: %s", black_score, white_score)
            self.show_error_dialog(
                f"Final score - Black: {black_score}, White: {white_score}"
            )
            self.show_error_dialog(self.controller.game_over_message)

        self.drawing_area.queue_draw()
        self.update_nb_pieces()
        self.update_play_history()
        if not self.controller.is_game_over:
            GLib.idle_add(self.controller.next_move)

    def update_nb_pieces(self):
        """
        Update the piece count labels.
        """
        self.black_nb_pieces.set_label(
            f"Black has {self.controller.get_pieces_count(Color.BLACK)} pieces"
        )
        self.white_nb_pieces.set_label(
            f"White has {self.controller.get_pieces_count(Color.WHITE)} pieces"
        )

    def update_timers_thread(self):
        """
        Background thread to update timer displays and check for time-outs.
        """
        if self.controller.is_blitz():
            while not self.controller.is_game_over:
                GLib.idle_add(self.update_timers)
                time.sleep(1)

    def update_timers(self):
        """
        Update the timer display labels.
        """
        self.black_timer_label.set_text(
            f"Black: {self.controller.display_time_player(Color.BLACK)}"
        )
        self.white_timer_label.set_text(
            f"White: {self.controller.display_time_player(Color.WHITE)}"
        )

    def update_play_history(self):
        """
        Update the play history list with the latest move.

        :param x: Column coordinate of the move
        :param y: Row coordinate of the move
        """
        last_play = self.controller.get_last_play()
        if last_play is None:
            return
        new_move = Gtk.Label(
            label=f"{last_play[4]} placed a piece at {chr(ord('A') + last_play[2])}{last_play[3] + 1}"
        )
        self.plays_list.prepend(new_move)
        if len(self.plays_list) > OthelloGUI.PLAYS_IN_HISTORY:
            self.plays_list.remove(self.plays_list.get_last_child())

    def draw(self, _area: Gtk.DrawingArea, cr: cairo.Context, width: int, height: int):
        """
        Master drawing function called by the DrawingArea.

        :param _area: The drawing area widget
        :param cr: Cairo context for drawing
        :param width: Width of the drawing area
        :param height: Height of the drawing area
        """
        self.draw_board(cr)
        self.draw_grid(cr)
        self.draw_pieces(cr)
        self.draw_legal_moves(cr)

    def draw_board(self, cr: cairo.Context):
        """
        Draws the green board background.

        :param cr: Cairo context for drawing
        """
        board_color = (0.2, 0.6, 0.2)
        cr.set_source_rgb(*board_color)
        cr.paint()

    def draw_grid(self, cr: cairo.Context):
        """
        Draws the grid lines on the board.

        :param cr: Cairo context for drawing
        """
        grid_color = (0.1, 0.4, 0.1)
        cr.set_line_width(1)
        cr.set_source_rgb(*grid_color)

        for x in range(self.grid_size + 1):
            cr.move_to(x * self.cell_size, 0)
            cr.line_to(x * self.cell_size, self.grid_size * self.cell_size)

        for y in range(self.grid_size + 1):
            cr.move_to(0, y * self.cell_size)
            cr.line_to(self.grid_size * self.cell_size, y * self.cell_size)

        cr.stroke()

    def draw_legal_moves(self, cr: cairo.Context):
        """
        Draws semi-transparent indicators for legal moves.

        :param cr: Cairo context for drawing
        """
        black_piece_color = (0, 0, 0, 0.3)
        white_piece_color = (1, 1, 1, 0.3)
        legal_moves = self.controller.get_possible_moves(
            self.controller.get_current_player()
        )

        color = (
            black_piece_color
            if self.controller.get_current_player() == Color.BLACK
            else white_piece_color
        )
        cr.set_source_rgba(*color)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if legal_moves.get(x, y):
                    center_x = x * self.cell_size + self.cell_size // 2
                    center_y = y * self.cell_size + self.cell_size // 2
                    radius = self.cell_size // 2 - 2
                    cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
                    cr.fill()

    def draw_pieces(self, cr: cairo.Context):
        """
        Draws all game pieces (black and white) on the board.

        :param cr: Cairo context for drawing
        """
        black_piece_color = (0, 0, 0)
        white_piece_color = (1, 1, 1)

        for x in range(self.grid_size):
            for y in range(self.grid_size):
                if not (
                    self.controller.get_position(Color.BLACK, x, y)
                    or self.controller.get_position(Color.WHITE, x, y)
                ):
                    continue

                center_x = x * self.cell_size + self.cell_size // 2
                center_y = y * self.cell_size + self.cell_size // 2
                radius = self.cell_size // 2 - 2

                if self.controller.get_position(Color.BLACK, x, y):
                    cr.set_source_rgb(*black_piece_color)
                else:
                    cr.set_source_rgb(*white_piece_color)

                cr.arc(center_x, center_y, radius, 0, 2 * math.pi)
                cr.fill()

    def board_click(self, _gesture, _n_press, click_x: float, click_y: float):
        """
        Handle clicks on the game board.

        :param _gesture: The gesture object (unused)
        :param _n_press: Number of presses (unused)
        :param click_x: X coordinate of the click
        :param click_y: Y coordinate of the click
        """
        if (
            self.controller.is_game_over
            or not self.controller.current_player_is_human()
        ):
            return
        board_x = int(click_x / self.cell_size)
        board_y = int(click_y / self.cell_size)
        if 0 <= board_x < self.grid_size and 0 <= board_y < self.grid_size:
            try:
                self.controller.play(board_x, board_y)
            except IllegalMoveException as err:
                self.logger.debug(err)

    def forfeit_handler(self, _button: Gtk.Button):
        """
        Handle forfeit button click.

        :param _button: The button widget (unused)
        """
        self.show_confirm_dialog(
            "Are you sure? This will close the program and your"
            " progression will be lost!",
            self.forfeit_handler_callback,
        )

    def forfeit_handler_callback(self, response):
        """
        Handle forfeit confirmation response.

        :param response: Dialog response value
        """
        if response == -5:  # OK button
            self.show_confirm_dialog(
                f"{(~self.controller.get_current_player()).name} wins the game",
                lambda _: self.quit(),
            )

    def restart_handler(self, _button: Gtk.Button):
        """
        Handle restart button click.

        :param _button: The button widget (unused)
        """
        self.show_confirm_dialog(
            "Are you sure you want to restart the game?", self.restart_handler_callback
        )

    def restart_handler_callback(self, confirmation):
        """
        Handle restart confirmation response.

        :param confirmation: Dialog response value
        """
        if confirmation == -5:  # OK button
            self.over = True
            if hasattr(self, "blitz_thread") and self.blitz_thread is not None:
                self.blitz_thread.join(timeout=1.0)
            self.controller.restart()
            for _ in range(len(self.plays_list)):
                self.plays_list.remove(self.plays_list.get_last_child())
            self.update_nb_pieces()
            self.over = False
            self.__init_game(self.controller)

    def file_chooser(self, callback, default_file_name: str, file_extension: str):
        """
        Show a file chooser dialog.

        :param callback: Function to call with the dialog result
        :param default_file_name: Default file name suggestion
        :param file_extension: File extension to filter by
        """
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
        """
        Handle save and quit button click.

        :param _button: The button widget (unused)
        """
        self.file_chooser(self.on_save_dialog_response, "my_game", "sav")

    def on_save_dialog_response(self, dialog, response):
        """
        Handle save dialog response.

        :param dialog: The dialog widget
        :param response: Dialog response value
        """
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self.save_game_to_file(file_path)
            self.close()
        dialog.destroy()

    def save_game_to_file(self, file_path):
        """
        Save the current game state to a file.

        :param file_path: Path to save the game
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                game_data = self.controller.export()
                file.write(game_data)
            logger.info("Game saved to %s", file_path)
        except IOError as e:
            self.show_error_dialog(f"Failed to save game: {str(e)}")
        except Exception as e:
            self.show_error_dialog(f"Unexpected error: {str(e)}")

    def save_history_handler(self, _button: Gtk.Button):
        """
        Handle save history button click.
        """
        self.file_chooser(self.on_save_history_dialog_response, "my_hist", "hist")

    def on_save_history_dialog_response(self, dialog, response):
        """
        Handle save history dialog response.

        :param dialog: The dialog widget
        :param response: Dialog response value
        """
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self.save_history_to_file(file_path)
        dialog.destroy()

    def save_history_to_file(self, file_path):
        """
        Save the game history to a file.

        :param file_path: Path to save the game history
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                game_data = self.controller.export_history()
                file.write(game_data)
            logger.info("Game history saved to %s", file_path)
        except IOError as e:
            self.show_error_dialog(f"Failed to save game history: {str(e)}")
        except Exception as e:
            self.show_error_dialog(f"Unexpected error: {str(e)}")

    def show_confirm_dialog(self, message, callback):
        """
        Show a confirmation dialog.

        :param message: The message to display
        :param callback: Function to call with the dialog result
        """

        def call_cb(dialog, response):
            dialog.destroy()
            callback(response)

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=message,
        )
        dialog.connect("response", call_cb)
        dialog.present()

    def show_error_dialog(self, message):
        """
        Display an error dialog with a given message.

        :param message: The error message to display in the dialog
        """

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=str(message),
        )
        dialog.connect("response", lambda d, _: d.destroy())
        dialog.present()
