from copy import deepcopy

import gi   
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gtk, GLib

class Automaton(Gtk.EventBox):
    def __init__(self):
        Gtk.EventBox.__init__(self)
        self._cells = []
        self._rows = 0
        self._columns = 0
        self._playing = False
        self._tick = 100
        self._tick_id = None
        self.connect('button-press-event', self.__clicked_cb)

    def __tick_cb(self):
        if not self._playing:
            return True
        next_cells = deepcopy(self._cells)
        for column in range(0, self._columns):
            for row in range(0, self._rows):
                next_cells[column][row] = self._get_next_state(column, row)
        self._cells = next_cells
        self.queue_draw()
        return True

    def _get_next_state(self, column, row):
        is_alive = self._cells[column][row]
        neighborhood = [
            (-1, -1), (0, -1), (+1, -1),
            (-1,  0), (0,  0), (+1,  0),
            (-1, +1), (0, +1), (+1, +1),
        ]

        neighbors = 0
        for neighbor in neighborhood:
            if neighbor[0] == 0 and neighbor[1] == 0:
                continue
            if self._get_safe_state(column + neighbor[0], row + neighbor[1]):
                neighbors += 1

        if is_alive and neighbors < 2:
            return False
        if is_alive and neighbors in [2,3]:
            return True
        if is_alive and neighbors > 3:
            return False
        if not is_alive and neighbors == 3:
            return True
        return False

    def _get_safe_state(self, column, row):
        column = column % self._columns
        row = row % self._rows
        return self._cells[column][row]

    def __clicked_cb(self, widget, event):
        alloc = self.get_allocation()
        cell_width = alloc.width / self._columns
        cell_height = alloc.height / self._rows

        cell_row = int(event.y / cell_height)
        cell_column = int(event.x / cell_width)
        self._cells[cell_column][cell_row] = not self._cells[cell_column][cell_row]

        self.queue_draw()

    def _draw_square(self, cr, x, y, width, height, r, g, b):
        cr.set_source_rgb(r, g, b);
        cr.rectangle(x, y, width, height);
        cr.fill();

    def do_draw(self, cr):
        alloc = self.get_allocation()
        width = alloc.width
        height = alloc.height

        self._draw_square(cr, 0, 0, width, height, 1, 1, 1)
        cell_width = width / self._columns
        cell_height = height / self._rows

        for column in range(0, self._columns):
            for row in range(0, self._rows):
                cell_x = column * cell_width
                cell_y = row * cell_height
                if self._cells[column][row] == True:
                    self._draw_square(cr, cell_x, cell_y, cell_width, cell_height, 0, 0, 0)

    def reset(self, rows=50, columns=50):
        self._rows = rows
        self._columns = columns
        self._cells = [[False for x in range(rows)] for y in range(columns)]
        self.queue_draw()

    def accelerate(self, tick):
        self._tick = tick
        if self._tick_id is not None:
            GLib.source_remove(self._tick_id)
        self._tick_id = GLib.timeout_add(self._tick, self.__tick_cb)


class Application(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)
        self.window = None

    def _setup_ui(self):
        self.window = Gtk.ApplicationWindow(application=self)
        self.window.set_default_size(512, 512)

        switch = Gtk.Switch()
        switch.connect('state-set', self.__switched_cb)

        reset = Gtk.Button.new_from_icon_name('view-refresh-symbolic', Gtk.IconSize.BUTTON)
        reset.connect('clicked', self.__reset_cb)

        bar = Gtk.HeaderBar()
        bar.set_show_close_button(True)
        bar.props.title = "Gnome of Life"
        bar.pack_start(switch)
        bar.pack_end(reset)

        self.automaton = Automaton()
        self.automaton.reset()
        self.automaton.accelerate(100)

        self.window.set_titlebar(bar)
        self.window.add(self.automaton)
        self.window.show_all()

    def __switched_cb(self, widget, state):
        self.automaton._playing = not self.automaton._playing

    def __reset_cb(self, widget):
        self.automaton.reset()

    def do_activate(self):
        if self.window is None:
            self._setup_ui()
        self.window.present()

    def on_quit(self, action, param):
        self.quit()

if __name__ == "__main__":
    app = Application()
    app.run()
