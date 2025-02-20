from gi.repository import Gtk, Gdk, GLib
import gi

gi.require_version("Gtk", "4.0")


class MyApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.jeu.othello")
        GLib.set_application_name("othello")
        self.grid_size = 8
        self.cell_size = 50

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_content_width(self.grid_size * self.cell_size)
        self.drawing_area.set_content_height(self.grid_size * self.cell_size)
        self.drawing_area.set_draw_func(self.draw)

        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("button_press_event", self.on_mouse_click)

    def do_activate(self):
        win = Gtk.ApplicationWindow(application=self, title="Othello")
        win.set_default_size(400, 400)
        win.present()

    def draw(self, ctx):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x, y = col * self.cell_size, row * self.cell_size
                ctx.rectangle(x, y, self.cell_size, self.cell_size)
                ctx.fill()

                """
                ctx.arc(x + self.cell_size / 2, y + self.cell_size / 2, self.cell_size / 3, 0, 2 * 3.14)
                ctx.fill()
                """

    def on_mouse_click(self, event):
        col = int(event.x // self.cell_size)
        row = int(event.y // self.cell_size)
        self.drawing_area.queue_draw()


app = MyApplication()
app.run()
