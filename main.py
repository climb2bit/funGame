import curses
import time

from sand.grid import Grid
from sand.renderer import Renderer, draw_splash, run
from sand.input_handler import InputHandler

TARGET_FPS = 30
FRAME_DURATION = 1.0 / TARGET_FPS


def _make_grid(rows: int, cols: int) -> Grid:
    return Grid(max(cols, 1), max(rows - 2, 1))


def game_main(stdscr) -> None:
    rows, cols = stdscr.getmaxyx()
    grid = _make_grid(rows, cols)
    renderer = Renderer(stdscr, grid)
    handler = InputHandler(stdscr, grid)

    draw_splash(stdscr)

    current_fps = TARGET_FPS

    while not handler.is_quit():
        frame_start = time.monotonic()

        handler.process()

        if not handler.is_paused():
            grid.tick()

        renderer.draw_grid()
        renderer.draw_hud(
            current_element=handler.get_current_element(),
            paused=handler.is_paused(),
            brush_size=handler.get_brush_size(),
            fps=current_fps,
        )

        try:
            stdscr.refresh()
        except curses.error:
            new_rows, new_cols = stdscr.getmaxyx()
            try:
                curses.resizeterm(new_rows, new_cols)
            except curses.error:
                pass
            old_grid = grid
            grid = _make_grid(new_rows, new_cols)
            # Copy old contents into new grid (cropped/padded)
            for y in range(min(old_grid.height, grid.height)):
                for x in range(min(old_grid.width, grid.width)):
                    grid.cells[y][x] = old_grid.cells[y][x]
                    grid.fire_age[y][x] = old_grid.fire_age[y][x]
                    grid.gas_age[y][x] = old_grid.gas_age[y][x]
            renderer.grid = grid
            handler.grid = grid
            grid.dirty = None  # force full redraw after resize
            continue

        elapsed = time.monotonic() - frame_start
        sleep_time = FRAME_DURATION - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)

        current_fps = round(1.0 / max(time.monotonic() - frame_start, 0.001))


if __name__ == "__main__":
    run(game_main)
