# Task 02 — Curses Renderer

## Goal
Build a cross-platform terminal renderer using Python's `curses` library (with `windows-curses` fallback on Windows). This module takes a `Grid` object and draws it to the terminal each frame.

---

## Output File
`sand/renderer.py`

---

## Dependencies
- Task 01 (`sand/grid.py`) must exist first
- External: `windows-curses` on Windows (auto-install logic included below)

---

## Cross-Platform Setup

### Windows Compatibility
At the top of `renderer.py`, add this import shim:

```python
import sys
try:
    import curses
except ImportError:
    if sys.platform == "win32":
        raise ImportError(
            "Run: pip install windows-curses"
        )
    raise
```

Also provide a `setup.py` or `requirements.txt` in the project root:

**`requirements.txt`:**
```
windows-curses; sys_platform == "win32"
```

---

## Color Mapping

Define a `COLORS` dict mapping `color_id` (from `ELEMENT_META` in grid.py) to a `(fg, bg)` curses color pair. Use these mappings:

| color_id | Element  | FG Color            | BG Color   |
|----------|----------|---------------------|------------|
| 0        | EMPTY    | BLACK               | BLACK      |
| 1        | SAND     | YELLOW              | BLACK      |
| 2        | WATER    | CYAN                | BLUE       |
| 3        | FIRE     | RED                 | YELLOW     |
| 4        | WOOD     | YELLOW (dark)       | BLACK      |
| 5        | STONE    | WHITE               | BLACK      |
| 6        | SMOKE    | WHITE (dim)         | BLACK      |
| 7        | STEAM    | CYAN (dim)          | BLACK      |

Initialize these as curses color pairs in `init_colors()`.

---

## Renderer Class

```python
class Renderer:
    def __init__(self, stdscr, grid: Grid)
    def init_colors(self) -> None
    def draw_grid(self) -> None
    def draw_hud(self, current_element: Element, paused: bool) -> None
    def get_playfield_size(self) -> tuple[int, int]  # (width, height)
```

### `__init__`
- Store `stdscr` and `grid` references
- Call `curses.curs_set(0)` to hide the cursor
- Call `init_colors()`
- Calculate the drawable playfield area:
  - Reserve **2 rows at the bottom** for the HUD
  - Playfield = full terminal width × (terminal height − 2)

### `init_colors`
- Call `curses.start_color()` and `curses.use_default_colors()`
- Register each color pair with `curses.init_pair(color_id, fg, bg)`

### `draw_grid`
- Iterate every `(x, y)` cell in the grid
- Look up the element's `char` and `color_id` from `ELEMENT_META`
- Call `stdscr.addch(y, x, char, curses.color_pair(color_id))`
- Clip to terminal bounds — never draw outside the terminal
- Use `stdscr.addch` with a try/except to silently ignore boundary errors (common at bottom-right corner of terminal)

### `draw_hud`
Draw a status bar in the last 2 rows:
- Row -2: `[ Q:Quit  R:Reset  P:Pause  Mouse:Draw  RClick:Erase ]`
- Row -1: `Current: <element name>   [ 1]SAND [ 2]WATER [ 3]FIRE [ 4]WOOD [ 5]STONE  <PAUSED>` (PAUSED shown only when paused)

### `get_playfield_size`
Return `(terminal_width, terminal_height - 2)` — what the `Grid` should be sized to.

---

## Entry Point Wrapper

Add a `run(main_fn)` helper:

```python
def run(main_fn):
    """Wraps curses.wrapper with Windows-safe error handling."""
    try:
        curses.wrapper(main_fn)
    except KeyboardInterrupt:
        pass
```

---

## Validation

Add a `if __name__ == "__main__"` block that:
1. Creates a small test `Grid(40, 20)`
2. Places a few elements at known positions
3. Runs the renderer for 2 seconds (just drawing, no tick)
4. Exits cleanly

```python
if __name__ == "__main__":
    import time
    from sand.grid import Grid, Element

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
```

---

## Notes
- Do NOT handle input in this file — that's Task 04
- The `Grid` size should match the renderer's `get_playfield_size()` — this wiring happens in Task 05
- On terminals without color support, degrade gracefully (catch `curses.error` in `init_colors`)
