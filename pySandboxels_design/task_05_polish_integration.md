# Task 05 — Polish & Integration

## Goal
Wire all modules together into a single runnable game (`main.py`). Add the game loop with frame timing, a polished HUD, startup screen, and a `README.md` with install/run instructions for Windows and Linux.

---

## Output Files
- `main.py` — entry point
- `README.md` — install and usage instructions

---

## Dependencies
All previous tasks must be complete:
- `sand/grid.py` (Task 01)
- `sand/renderer.py` (Task 02)
- `sand/physics.py` (Task 03)
- `sand/input_handler.py` (Task 04)

---

## Final Project Structure

```
falling-sand/
  main.py
  requirements.txt
  README.md
  sand/
    __init__.py
    grid.py
    renderer.py
    physics.py
    input_handler.py
```

---

## `main.py`

### Imports
```python
import curses
import time
from sand.grid import Grid, Element
from sand.renderer import Renderer, run
from sand.input_handler import InputHandler
```

### Constants
```python
TARGET_FPS = 30
FRAME_DURATION = 1.0 / TARGET_FPS
```

### `game_main(stdscr)`

This is the function passed to `curses.wrapper`. It should:

1. **Detect terminal size** using `stdscr.getmaxyx()` → `(rows, cols)`
2. **Create grid** sized to the playfield: `Grid(cols, rows - 2)`
   - The `-2` reserves space for the HUD at the bottom
3. **Create renderer**: `Renderer(stdscr, grid)`
4. **Create input handler**: `InputHandler(stdscr, grid)`
5. **Show splash screen** for 1.5 seconds (see below)
6. **Enter game loop**:

```python
while not handler.is_quit():
    frame_start = time.monotonic()

    # Input
    handler.process()

    # Physics (skip if paused)
    if not handler.is_paused():
        grid.tick()

    # Render
    stdscr.erase()
    renderer.draw_grid()
    renderer.draw_hud(
        current_element=handler.get_current_element(),
        paused=handler.is_paused(),
        brush_size=handler.get_brush_size(),
        fps=current_fps,
    )
    stdscr.refresh()

    # Frame timing
    elapsed = time.monotonic() - frame_start
    sleep_time = FRAME_DURATION - elapsed
    if sleep_time > 0:
        time.sleep(sleep_time)

    current_fps = round(1.0 / max(time.monotonic() - frame_start, 0.001))
```

### `if __name__ == "__main__"`
```python
if __name__ == "__main__":
    run(game_main)
```

---

## Splash Screen

In `renderer.py`, add a `draw_splash(stdscr)` function (called before the loop):

```
╔══════════════════════════════╗
║    🏖  Falling Sand CLI      ║
║                              ║
║  1-7  : Select element       ║
║  Mouse: Draw / RClick erase  ║
║  [ ]  : Change brush size    ║
║  P    : Pause                ║
║  R    : Reset                ║
║  Q    : Quit                 ║
║                              ║
║     Press any key to start   ║
╚══════════════════════════════╝
```

Center this box in the terminal. Wait for a keypress (`stdscr.getch()`). Then clear and start the game.

Use ASCII box chars (`+`, `-`, `|`) as fallback if Unicode box chars aren't supported (catch `curses.error`).

---

## Enhanced HUD

Update `Renderer.draw_hud()` to accept `brush_size` and `fps` parameters.

**Row -2 (controls bar):**
```
 Q:Quit  R:Reset  P:Pause  1-7:Element  [/]:Brush
```

**Row -1 (status bar):**
```
 Element: SAND  Brush: ■■□□□  FPS: 28   ⏸ PAUSED
```

Brush size visual: filled squares for active size, empty for max:
- Size 1: `■□□□□`
- Size 2: `■■□□□`
- Size 3: `■■■□□`

Show `⏸ PAUSED` (or `[PAUSED]` as ASCII fallback) only when paused, in a highlighted color.

---

## Handle Terminal Resize

In the game loop, catch `curses.error` on `stdscr.refresh()` and gracefully handle resize:

```python
try:
    stdscr.refresh()
except curses.error:
    curses.resizeterm(*stdscr.getmaxyx())
```

On resize, recreate the grid at the new size. Optionally copy the old grid contents into the new one (cropped or padded).

---

## `README.md`

````markdown
# Falling Sand — CLI Edition

A terminal-based falling-sand simulator. Drop sand, water, fire, and more — watch them interact in real time.

## Requirements
- Python 3.8+
- Windows: requires `windows-curses`

## Install

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

> Tip: Use Windows Terminal or PowerShell for best results. Avoid the old cmd.exe — color support is limited.

## Controls

| Input           | Action                     |
|-----------------|----------------------------|
| Mouse drag      | Draw element               |
| Right drag      | Erase                      |
| 1–7             | Select element             |
| E / Shift+E     | Cycle elements             |
| `[` / `]`       | Decrease / increase brush  |
| P               | Pause / Resume             |
| R               | Reset canvas               |
| Q               | Quit                       |
| Arrow + Space   | Keyboard cursor (no mouse) |

## Elements

| Key | Element | Behaviour                        |
|-----|---------|----------------------------------|
| 1   | Sand    | Falls, piles, sinks in water     |
| 2   | Water   | Flows sideways, fills containers |
| 3   | Fire    | Spreads, burns wood, boils water |
| 4   | Wood    | Solid, flammable                 |
| 5   | Stone   | Inert wall                       |
| 6   | Smoke   | Rises, dissipates                |
| 7   | Steam   | Rises from water + fire          |

## Troubleshooting

**Colors not showing on Windows:** Use Windows Terminal (not cmd.exe).  
**Mouse not working:** Use keyboard mode — arrow keys + Space to draw.  
**UnicodeDecodeError on startup:** Run `chcp 65001` in cmd.exe before launching.  
**Small terminal:** Maximize your window — the grid fills available space automatically.
````

---

## Final Validation Checklist

Before marking this task done, verify:

- [ ] `python main.py` launches without error on Linux
- [ ] `python main.py` launches without error on Windows (with `windows-curses` installed)
- [ ] Sand falls and piles correctly
- [ ] Water spreads horizontally and fills containers
- [ ] Fire spreads to adjacent wood
- [ ] Water near fire produces steam
- [ ] Smoke rises and fades
- [ ] Mouse drawing works (or keyboard fallback)
- [ ] Pause stops simulation but keeps rendering
- [ ] Reset clears the grid
- [ ] Quit exits cleanly without terminal corruption
- [ ] HUD shows current element, brush size, FPS
- [ ] Terminal resize doesn't crash the game
