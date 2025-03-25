from othello.gui import OthelloGUI
from othello.othello_board import OthelloBoard, Color, BoardSize
from gi.repository import Gtk, GLib, Gdk
import unittest
import time
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')


# VARIABLES

size = BoardSize.from_value(8)
loop = GLib.MainLoop()
timeout_id = None

test_state = {
    "board": None,
    "app": None,
    "window": None
}

# SET UP


def setup_test(with_blitz=False, time_limit=None):
    test_state["board"] = OthelloBoard(size)

    if with_blitz and time_limit:
        test_state["app"] = OthelloGUI(
            test_state["board"], time_limit=time_limit)
    else:
        test_state["app"] = OthelloGUI(test_state["board"])

    test_state["window"] = None


def activating(app):
    windows = app.get_windows()
    if windows:
        test_state["window"] = windows[0]
        add_timeout()


def add_timeout():
    global timeout_id
    timeout_id = GLib.timeout_add(500, check_window)


def check_window():
    if test_state["window"] is not None:
        try:
            test_state["current_test_function"]()
        finally:
            test_state["app"].quit()
            loop.quit()
            GLib.timeout_add(100, force_window_close)
        return GLib.SOURCE_REMOVE
    return GLib.SOURCE_CONTINUE


def force_window_close():
    if test_state["window"] is not None:
        test_state["window"].close()
    return GLib.SOURCE_REMOVE


def launch_app():
    test_state["app"].connect('activate', activating)
    test_state["app"].run([])


def simulate_board_click(x, y):
    window = test_state["window"]

    board_x = x * window.cell_size + (window.cell_size // 2)
    board_y = y * window.cell_size + (window.cell_size // 2)
    window.board_click(None, None, board_x, board_y)


# TESTS

def test_window_layout():
    setup_test()
    test_state["current_test_function"] = run_window_layout_test
    launch_app()


def run_window_layout_test():
    window = test_state["window"]

    # title
    assert window is not None
    assert window.get_title() == "Othello"

    # window size
    width, height = window.get_default_size()
    assert width == 800
    assert height == 600

    # main components
    child = window.get_child()
    assert child is not None
    assert isinstance(child, Gtk.Box)

    # drawing area
    assert window.drawing_area is not None
    assert window.drawing_area.get_content_width() == window.grid_size * \
        window.cell_size
    assert window.drawing_area.get_content_height() == window.grid_size * \
        window.cell_size

    # labels and buttons
    assert window.black_nb_pieces is not None
    assert window.white_nb_pieces is not None
    assert window.plays_list is not None
    assert window.forfeit_button is not None
    assert window.save_quit_button is not None
    assert window.restart_button is not None
    assert window.save_history_button is not None

    # button labels
    assert window.forfeit_button.get_label() == "forfeit"
    assert window.save_quit_button.get_label() == "save and quit"
    assert window.restart_button.get_label() == "restart"
    assert window.save_history_button.get_label() == "save history"

    # initial player counts
    assert window.black_nb_pieces.get_label() == "Black has 2 pieces"
    assert window.white_nb_pieces.get_label() == "White has 2 pieces"


def test_blitz_mode():
    setup_test(with_blitz=True, time_limit=300)
    test_state["current_test_function"] = run_blitz_mode_test
    launch_app()


def run_blitz_mode_test():
    window = test_state["window"]

    # blitz timer
    assert window.blitz_timer is not None
    assert window.black_timer_label is not None
    assert window.white_timer_label is not None
    assert window.is_blitz is True
    assert window.time_limit == 300

    # timer labels
    black_label_text = window.black_timer_label.get_text()
    white_label_text = window.white_timer_label.get_text()
    assert black_label_text.startswith("Black:")
    assert white_label_text.startswith("White:")


def test_input():
    setup_test()
    test_state["current_test_function"] = run_input_test
    launch_app()


def run_input_test():
    window = test_state["window"]
    board = test_state["board"]

    # init
    assert board.current_player == Color.BLACK
    assert window.plays_list.length == 0

    # valid move (2, 3) for BLACK
    initial_black_count = board.black.popcount()
    simulate_board_click(2, 3)

    assert board.current_player == Color.WHITE  # switch player
    assert window.plays_list.length == 1  # history updated

    # valid move (2, 2) for WHITE
    initial_white_count = board.white.popcount()
    simulate_board_click(2, 2)

    assert board.current_player == Color.BLACK
    assert window.plays_list.length == 2

    # invalid move, should not change state
    simulate_board_click(0, 0)
    assert board.current_player == Color.BLACK
    assert window.plays_list.length == 2

    # test button click
    original_show_confirm = window.show_confirm_dialog
    window.show_confirm_dialog = lambda msg, callback: None

    # forfeit
    window.forfeit_handler(None)

    # restart
    window.restart_handler(None)

    # Restore the original method
    window.show_confirm_dialog = original_show_confirm


def test_ui_updates():
    setup_test()
    test_state["current_test_function"] = run_ui_updates_test
    launch_app()


def run_ui_updates_test():
    window = test_state["window"]

    # initial piece counts
    initial_black_label = window.black_nb_pieces.get_label()
    initial_white_label = window.white_nb_pieces.get_label()

    # valid move
    board_x = 2 * window.cell_size + (window.cell_size // 2)
    board_y = 3 * window.cell_size + (window.cell_size // 2)
    window.board_click(None, None, board_x, board_y)

    # labels updated
    updated_black_label = window.black_nb_pieces.get_label()
    updated_white_label = window.white_nb_pieces.get_label()

    assert initial_black_label != updated_black_label
    assert initial_white_label != updated_white_label

    # history updated
    assert window.plays_list.length == 1

    # another move
    board_x = 2 * window.cell_size + (window.cell_size // 2)
    board_y = 2 * window.cell_size + (window.cell_size // 2)
    window.board_click(None, None, board_x, board_y)

    # history updated again
    assert window.plays_list.length == 2
