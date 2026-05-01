# Task 01 — Core Grid Engine

## Goal
Create the foundational data structures and element definitions for the falling-sand simulator. This module is pure logic — no rendering, no input. Everything else will be built on top of it.

---

## Output File
`sand/grid.py`

---

## Requirements

### 1. Element Enum
Define an `Element` enum (or named integer constants) with at least these types:

| ID | Name    | Notes                        |
|----|---------|------------------------------|
| 0  | EMPTY   | Air / nothing                |
| 1  | SAND    | Granular, falls down         |
| 2  | WATER   | Liquid, flows sideways       |
| 3  | FIRE    | Spreads, short-lived         |
| 4  | WOOD    | Solid, flammable             |
| 5  | STONE   | Solid, inert wall            |
| 6  | SMOKE   | Gas, rises                   |
| 7  | STEAM   | Gas, rises (from water+fire) |

Store element metadata (color, display char, name string) in a dict keyed by element ID — this will be consumed by the renderer later.

Example metadata structure:
```python
ELEMENT_META = {
    Element.SAND:  {"char": "█", "color_id": 3, "name": "Sand"},
    Element.WATER: {"char": "~", "color_id": 4, "name": "Water"},
    ...
}
```

### 2. Grid Class
Create a `Grid` class with the following:

**Constructor:**
```python
Grid(width: int, height: int)
```
- Stores a 2D array (list of lists, or `numpy` array if available) of element IDs
- Defaults all cells to `Element.EMPTY`
- Stores width and height

**Methods:**
```python
def get(self, x: int, y: int) -> Element
def set(self, x: int, y: int, element: Element) -> None
def in_bounds(self, x: int, y: int) -> bool
def clear(self) -> None
```

- `get` and `set` must do bounds checking — return `Element.STONE` for out-of-bounds reads (treat walls as solid), silently ignore out-of-bounds writes
- `clear` resets all cells to `Element.EMPTY`

### 3. Tick System
Add an `updated` 2D boolean array (same size as the grid) to track which cells have already been processed this tick. This prevents a particle from being moved twice in one frame.

Add a `tick()` method to `Grid` that:
1. Resets the `updated` array to all `False`
2. Iterates cells **bottom to top, left to right** (bottom-up so falling particles don't cascade in a single frame)
3. For each cell, calls `_update_cell(x, y)`
4. `_update_cell` dispatches to the correct physics function based on element type

At this stage, `_update_cell` can be a stub that does nothing — physics rules come in Task 03.

```python
def tick(self) -> None: ...
def _update_cell(self, x: int, y: int) -> None: ...  # stub for now
```

### 4. Helper: Swap
Add a private method:
```python
def _swap(self, x1, y1, x2, y2) -> None
```
Swaps two cells and marks both as updated.

---

## File Structure
```
sand/
  __init__.py      ← empty
  grid.py          ← this task
```

Create the `sand/` package folder and an empty `__init__.py` alongside `grid.py`.

---

## Do NOT include yet
- Any curses / terminal code
- Any input handling
- Actual physics logic (stubs only)

---

## Validation
After writing the file, add a `if __name__ == "__main__"` block that:
1. Creates a `Grid(20, 10)`
2. Sets a few cells to different elements
3. Calls `tick()` once
4. Prints the grid as a simple ASCII grid to stdout using `get()`

This lets us sanity-check the grid works before wiring up the renderer.
