import sys
try:
    import curses
except ImportError:
    if sys.platform == "win32":
        raise ImportError("Run: pip install windows-curses")
    raise

from sand.grid import Grid, Element, ELEMENT_META

# color_id -> (fg, bg) curses color constants
COLORS = {
    0: (curses.COLOR_BLACK,  curses.COLOR_BLACK),   # EMPTY
    1: (curses.COLOR_YELLOW, curses.COLOR_BLACK),   # SAND
    2: (curses.COLOR_CYAN,   curses.COLOR_BLUE),    # WATER
    3: (curses.COLOR_RED,    curses.COLOR_YELLOW),  # FIRE
    4: (curses.COLOR_YELLOW, curses.COLOR_BLACK),   # WOOD  (same fg, dimmed via attr)
    5: (curses.COLOR_WHITE,  curses.COLOR_BLACK),   # STONE
    6: (curses.COLOR_WHITE,  curses.COLOR_BLACK),   # SMOKE (dimmed via attr)
    7: (curses.COLOR_CYAN,   curses.COLOR_BLACK),   # STEAM (dimmed via attr)
}

# color_ids that should render dim
_DIM_IDS = {4, 6, 7}


class Renderer:
    def __init__(self, stdscr, grid: Grid):
        self.stdscr = stdscr
        self.grid = grid
        curses.curs_set(0)
        self.init_colors()

    def init_colors(self) -> None:
        try:
            curses.start_color()
            curses.use_default_colors()
            for color_id, (fg, bg) in COLORS.items():
                curses.init_pair(color_id, fg, bg)
        except curses.error:
            pass  # degrade gracefully on terminals without color support

    def _draw_cell(self, x: int, y: int) -> None:
        elem = self.grid.cells[y][x]
        meta = ELEMENT_META[elem]
        color_id = meta["color_id"]
        attr = curses.color_pair(color_id)
        if color_id in _DIM_IDS:
            attr |= curses.A_DIM
        try:
            self.stdscr.addch(y, x, meta["char"], attr)
        except curses.error:
            pass

    def draw_grid(self) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        playfield_h = max_y - 2
        grid = self.grid

        if grid.dirty is None:
            # Full redraw (first frame, after clear, or after resize).
            for y in range(min(grid.height, playfield_h)):
                for x in range(min(grid.width, max_x)):
                    self._draw_cell(x, y)
            grid.dirty = set()
        else:
            for x, y in grid.dirty:
                if 0 <= x < max_x and 0 <= y < playfield_h:
                    self._draw_cell(x, y)
            grid.dirty.clear()

    def draw_hud(self, current_element: Element, paused: bool,
                 brush_size: int = 1, fps: int = 0) -> None:
        max_y, max_x = self.stdscr.getmaxyx()
        controls = " Q:Quit  R:Reset  P:Pause  1-7:Element  [/]:Brush"
        elem_name = ELEMENT_META[current_element]["name"]
        brush_bar = "■" * brush_size + "□" * (5 - brush_size)
        status_line = f" Element: {elem_name:<6}  Brush: {brush_bar}  FPS: {fps}"
        if paused:
            try:
                status_line += "   ⏸ PAUSED"
            except Exception:
                status_line += "   [PAUSED]"

        width = max_x - 1
        try:
            self.stdscr.addstr(max_y - 2, 0, controls[:width].ljust(width))
        except curses.error:
            pass
        try:
            line = status_line[:width].ljust(width)
            attr = curses.A_REVERSE if paused else curses.A_NORMAL
            self.stdscr.addstr(max_y - 1, 0, line, attr)
        except curses.error:
            pass

    def get_playfield_size(self) -> tuple:
        max_y, max_x = self.stdscr.getmaxyx()
        return (max_x, max_y - 2)


def draw_splash(stdscr) -> None:
    max_y, max_x = stdscr.getmaxyx()
    lines = [
        "+==============================+",
        "|    Falling Sand CLI          |",
        "|                              |",
        "|  1-7  : Select element       |",
        "|  Mouse: Draw / RClick erase  |",
        "|  [ ]  : Change brush size    |",
        "|  P    : Pause                |",
        "|  R    : Reset                |",
        "|  Q    : Quit                 |",
        "|                              |",
        "|     Press any key to start   |",
        "+==============================+",
    ]
    start_y = max(0, (max_y - len(lines)) // 2)
    start_x = max(0, (max_x - len(lines[0])) // 2)
    for i, line in enumerate(lines):
        try:
            stdscr.addstr(start_y + i, start_x, line[:max_x - start_x - 1])
        except curses.error:
            pass
    stdscr.refresh()
    stdscr.nodelay(False)
    stdscr.getch()
    stdscr.nodelay(True)
    stdscr.erase()


def run(main_fn):
    """Wraps curses.wrapper with Windows-safe error handling."""
    try:
        curses.wrapper(main_fn)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    import time

    def test_main(stdscr):
        grid = Grid(40, 20)
        grid.set(10, 5, Element.SAND)
        grid.set(15, 3, Element.WATER)
        grid.set(20, 10, Element.FIRE)
        renderer = Renderer(stdscr, grid)
        renderer.draw_grid()
        renderer.draw_hud(Element.SAND, paused=False)
        stdscr.refresh()
        time.sleep(2)

    run(test_main)
