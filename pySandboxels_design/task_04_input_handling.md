# Task 04 — Input Handling

## Goal
Implement keyboard and mouse input handling in a dedicated module. This includes element switching, drawing/erasing on the grid, pause/reset, and brush size control — all cross-platform.

---

## Output File
`sand/input_handler.py`

---

## Dependencies
- Task 01 (`sand/grid.py`) must be complete
- Task 02 (`sand/renderer.py`) must be complete (for terminal size info)

---

## Cross-Platform Mouse Notes

Curses mouse support works on both Windows and Linux **with caveats**:
- On **Linux/macOS**: `curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)` enables full tracking
- On **Windows** (`windows-curses`): Mouse support is more limited — button clicks work but motion-while-pressed may not report correctly on all terminals
- **Fallback**: If mouse is unavailable, keyboard arrow keys + Enter to place elements must work as a fallback

---

## InputHandler Class

```python
class InputHandler:
    def __init__(self, stdscr, grid: Grid)
    def setup_mouse(self) -> bool          # returns True if mouse available
    def process(self) -> str               # returns action string or ""
    def get_current_element(self) -> Element
    def get_brush_size(self) -> int
    def is_paused(self) -> bool
    def is_quit(self) -> bool
```

### State to track:
```python
self.current_element: Element = Element.SAND
self.brush_size: int = 1          # 1 = single cell, 2 = 3x3, 3 = 5x5
self.paused: bool = False
self.quit: bool = False
self.cursor_x: int = 0            # keyboard cursor position
self.cursor_y: int = 0
self.mouse_available: bool
self.drawing: bool = False         # True while mouse button held
self.erasing: bool = False         # True while right mouse button held
```

---

## Keyboard Bindings

| Key         | Action                                 |
|-------------|----------------------------------------|
| `1`         | Select SAND                            |
| `2`         | Select WATER                           |
| `3`         | Select FIRE                            |
| `4`         | Select WOOD                            |
| `5`         | Select STONE                           |
| `6`         | Select SMOKE                           |
| `7`         | Select STEAM                           |
| `p` / `P`   | Toggle pause                           |
| `r` / `R`   | Reset / clear grid                     |
| `q` / `Q`   | Quit                                   |
| `[`         | Decrease brush size (min 1)            |
| `]`         | Increase brush size (max 5)            |
| Arrow keys  | Move keyboard cursor (fallback mode)   |
| `Space`     | Place current element at cursor (fallback) |
| `Backspace` | Erase at cursor (fallback)             |
| `e` / `E`   | Cycle through elements forward/back    |

---

## Mouse Handling

### Setup
```python
def setup_mouse(self) -> bool:
    try:
        curses.mousemask(
            curses.BUTTON1_PRESSED | curses.BUTTON1_RELEASED |
            curses.BUTTON3_PRESSED | curses.BUTTON3_RELEASED |
            curses.REPORT_MOUSE_POSITION |
            curses.BUTTON1_CLICKED | curses.BUTTON3_CLICKED
        )
        return True
    except:
        return False
```

### Processing mouse events
In `process()`, handle `curses.KEY_MOUSE`:
```python
_, mx, my, _, bstate = curses.getmouse()
```

- `BUTTON1_PRESSED` → set `self.drawing = True`
- `BUTTON1_RELEASED` → set `self.drawing = False`
- `BUTTON3_PRESSED` → set `self.erasing = True`
- `BUTTON3_RELEASED` → set `self.erasing = False`
- If `drawing` → call `_paint(mx, my, self.current_element)`
- If `erasing` → call `_paint(mx, my, Element.EMPTY)`

### `_paint(x, y, element)`
Paint the element at `(x, y)` with current brush size:
- Brush size 1 → single cell
- Brush size 2 → 3×3 area centered on `(x, y)`
- Brush size 3 → 5×5 area centered on `(x, y)`
- Formula: radius = `brush_size - 1`, paint all cells where `abs(dx) <= radius and abs(dy) <= radius`
- Clamp to grid bounds

---

## `process()` Method

This is the main method called once per frame. It should:

1. Call `stdscr.nodelay(True)` once (non-blocking input — do this in `__init__`)
2. Try `stdscr.getch()` — if `-1`, no key was pressed
3. Dispatch based on key value
4. Return a string describing what happened (for debugging), or `""` if nothing

```python
def process(self) -> str:
    key = self.stdscr.getch()
    if key == -1:
        return ""
    # ... dispatch
```

**Important**: Use `curses.KEY_MOUSE` to detect mouse events and call `curses.getmouse()` inside a try/except.

---

## Element Cycling Helper

```python
ELEMENT_ORDER = [
    Element.SAND, Element.WATER, Element.FIRE,
    Element.WOOD, Element.STONE, Element.SMOKE, Element.STEAM
]

def _cycle_element(self, direction: int = 1) -> None:
    idx = ELEMENT_ORDER.index(self.current_element)
    self.current_element = ELEMENT_ORDER[(idx + direction) % len(ELEMENT_ORDER)]
```

---

## Keyboard Cursor (Fallback Mode)

When `self.mouse_available` is False, draw a visible cursor using the renderer.
Track `self.cursor_x`, `self.cursor_y` — arrow keys move it, Space paints, Backspace erases.

The cursor position should be accessible to the renderer so it can highlight the cell (invert colors or use a special char like `+`).

---

## Validation

Add a `if __name__ == "__main__"` block:

```python
if __name__ == "__main__":
    import curses
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
```

At this point you should be able to draw elements with mouse/keyboard and see them render — but they won't move yet (physics not ticked).
