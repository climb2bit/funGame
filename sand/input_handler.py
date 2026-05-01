import sys
try:
    import curses
except ImportError:
    if sys.platform == "win32":
        raise ImportError("Run: pip install windows-curses")
    raise

from sand.grid import Grid, Element

ELEMENT_ORDER = [
    Element.SAND, Element.WATER, Element.FIRE,
    Element.WOOD, Element.STONE, Element.SMOKE, Element.STEAM,
]

_KEY_ELEMENT = {
    ord('1'): Element.SAND,
    ord('2'): Element.WATER,
    ord('3'): Element.FIRE,
    ord('4'): Element.WOOD,
    ord('5'): Element.STONE,
    ord('6'): Element.SMOKE,
    ord('7'): Element.STEAM,
}


class InputHandler:
    def __init__(self, stdscr, grid: Grid):
        self.stdscr = stdscr
        self.grid = grid

        self.current_element: Element = Element.SAND
        self.brush_size: int = 1
        self.paused: bool = False
        self.quit: bool = False
        self.cursor_x: int = 0
        self.cursor_y: int = 0
        self.drawing: bool = False
        self.erasing: bool = False
        self._last_mx: int = -1
        self._last_my: int = -1

        stdscr.nodelay(True)
        self.mouse_available: bool = self.setup_mouse()

    def setup_mouse(self) -> bool:
        try:
            curses.mousemask(
                curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED |
                curses.BUTTON3_PRESSED | curses.BUTTON3_RELEASED |
                curses.REPORT_MOUSE_POSITION |
                curses.BUTTON1_CLICKED | curses.BUTTON3_CLICKED
            )
            return True
        except Exception:
            return False

    def get_current_element(self) -> Element:
        return self.current_element

    def get_brush_size(self) -> int:
        return self.brush_size

    def is_paused(self) -> bool:
        return self.paused

    def is_quit(self) -> bool:
        return self.quit

    def _paint(self, x: int, y: int, element: Element) -> None:
        radius = self.brush_size - 1
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                self.grid.set(x + dx, y + dy, element)

    def _paint_line(self, x0: int, y0: int, x1: int, y1: int, element: Element) -> None:
        """Bresenham's line — paint all cells between two mouse positions."""
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self._paint(x0, y0, element)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def _handle_mouse_event(self, mx: int, my: int, bstate: int) -> None:
        if bstate & curses.BUTTON1_PRESSED:
            self.drawing = True
        if bstate & curses.BUTTON1_RELEASED:
            self.drawing = False
        if bstate & curses.BUTTON3_PRESSED:
            self.erasing = True
        if bstate & curses.BUTTON3_RELEASED:
            self.erasing = False

        element = None
        if self.drawing or (bstate & (curses.BUTTON1_PRESSED | curses.BUTTON1_CLICKED)):
            element = self.current_element
        elif self.erasing or (bstate & (curses.BUTTON3_PRESSED | curses.BUTTON3_CLICKED)):
            element = Element.EMPTY

        if element is not None:
            if self._last_mx >= 0:
                self._paint_line(self._last_mx, self._last_my, mx, my, element)
            else:
                self._paint(mx, my, element)

        self._last_mx = mx
        self._last_my = my

        if bstate & curses.BUTTON1_RELEASED:
            self._last_mx = -1
            self._last_my = -1
        if bstate & curses.BUTTON3_RELEASED:
            self._last_mx = -1
            self._last_my = -1

    def _cycle_element(self, direction: int = 1) -> None:
        idx = ELEMENT_ORDER.index(self.current_element)
        self.current_element = ELEMENT_ORDER[(idx + direction) % len(ELEMENT_ORDER)]

    def process(self) -> str:
        last_action = ""
        # Drain all queued events so fast drags don't drop positions.
        while True:
            key = self.stdscr.getch()
            if key == -1:
                break

            if key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    self._handle_mouse_event(mx, my, bstate)
                    last_action = "mouse"
                except curses.error:
                    pass
                continue

            # Keyboard events — process once and stop draining.
            if key in _KEY_ELEMENT:
                self.current_element = _KEY_ELEMENT[key]
                last_action = f"select {self.current_element.name}"
            elif key in (ord('p'), ord('P')):
                self.paused = not self.paused
                last_action = "pause"
            elif key in (ord('r'), ord('R')):
                self.grid.clear()
                last_action = "reset"
            elif key in (ord('q'), ord('Q')):
                self.quit = True
                last_action = "quit"
            elif key == ord('['):
                self.brush_size = max(1, self.brush_size - 1)
                last_action = f"brush {self.brush_size}"
            elif key == ord(']'):
                self.brush_size = min(5, self.brush_size + 1)
                last_action = f"brush {self.brush_size}"
            elif key == ord('e'):
                self._cycle_element(1)
                last_action = f"cycle {self.current_element.name}"
            elif key == ord('E'):
                self._cycle_element(-1)
                last_action = f"cycle {self.current_element.name}"
            elif key == curses.KEY_UP:
                self.cursor_y = max(0, self.cursor_y - 1)
            elif key == curses.KEY_DOWN:
                self.cursor_y = min(self.grid.height - 1, self.cursor_y + 1)
            elif key == curses.KEY_LEFT:
                self.cursor_x = max(0, self.cursor_x - 1)
            elif key == curses.KEY_RIGHT:
                self.cursor_x = min(self.grid.width - 1, self.cursor_x + 1)
            elif key == ord(' '):
                self._paint(self.cursor_x, self.cursor_y, self.current_element)
                last_action = "place"
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                self._paint(self.cursor_x, self.cursor_y, Element.EMPTY)
                last_action = "erase"
            break

        return last_action


if __name__ == "__main__":
    from sand.grid import Grid, Element
    from sand.renderer import Renderer, run

    def test_main(stdscr):
        grid = Grid(60, 30)
        renderer = Renderer(stdscr, grid)
        handler = InputHandler(stdscr, grid)

        while not handler.is_quit():
            handler.process()
            renderer.draw_grid()
            renderer.draw_hud(handler.get_current_element(), handler.is_paused())
            stdscr.refresh()

    run(test_main)
