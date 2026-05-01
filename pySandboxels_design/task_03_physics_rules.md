# Task 03 — Physics Rules

## Goal
Implement the per-element physics update functions and wire them into the `Grid._update_cell()` dispatch method from Task 01. This is the heart of the simulation.

---

## Output File
`sand/physics.py`  
(also modifies `sand/grid.py` to import and wire in the dispatch)

---

## Dependencies
- Task 01 (`sand/grid.py`) must be complete

---

## General Rules

- **Never move a cell that's already been marked `updated`** — always check `self.updated[y][x]` before processing
- **Mark cells as updated** when they move using `_swap()` (which already handles this) or manually set `self.updated[y][x] = True`
- **Randomness**: Use `random.randint` / `random.choice` for probabilistic behaviors — do NOT import numpy for this
- **Bottom-up iteration**: Already handled by `Grid.tick()` — physics functions can assume the rows below have already been processed this frame

---

## Physics Functions

Each function has the signature:
```python
def update_<element>(grid: Grid, x: int, y: int) -> None
```

---

### `update_sand(grid, x, y)`
Sand is a granular solid — it falls and piles.

1. If cell below `(x, y+1)` is `EMPTY` or `WATER` → swap (sand sinks through water)
2. Else, randomly try `(x-1, y+1)` or `(x+1, y+1)` — if either is `EMPTY` or `WATER` → swap
3. Otherwise, stay put

```
Priority: down → random diagonal down-left or down-right
```

---

### `update_water(grid, x, y)`
Water is a liquid — it falls and spreads horizontally.

1. If `(x, y+1)` is `EMPTY` → move down
2. Else, shuffle `[left, right]` randomly, try each:
   - If `(x±1, y)` is `EMPTY` → move there
3. Otherwise, stay

```
Priority: down → random left or right (equal probability)
```

---

### `update_fire(grid, x, y)`
Fire is energetic — it spreads, consumes, and dies.

1. **Lifetime**: Fire has a random lifetime (e.g. 20–60 ticks). Track this using a parallel `grid.metadata[y][x]` dict or a simple integer array `grid.fire_age` of same shape as the grid. Decrement each tick.
   - When lifetime hits 0: replace with `SMOKE` (50% chance) or `EMPTY` (50%)
2. **Spread**: For each of the 4 neighbors `(x±1, y)` and `(x, y±1)`:
   - If neighbor is `WOOD` → 5% chance per tick to ignite it (set to `FIRE`, reset its lifetime)
   - If neighbor is `WATER` → 30% chance to turn neighbor into `STEAM`, extinguish this fire cell (`EMPTY`)
3. **Move**: Fire does not move on its own (it spreads by igniting neighbors)

**Implementation note for fire age:**  
Add `self.fire_age` as a 2D integer array (same dimensions as grid) to `Grid.__init__`. Initialize all to 0. When a cell is set to `FIRE`, also set `fire_age[y][x]` to a random value between 20 and 60.

Modify `Grid.set()` to handle this:
```python
def set(self, x, y, element):
    ...
    if element == Element.FIRE:
        self.fire_age[y][x] = random.randint(20, 60)
    ...
```

---

### `update_wood(grid, x, y)`
Wood is a solid — it doesn't move. No update logic needed beyond being a valid target for fire.

```python
def update_wood(grid, x, y) -> None:
    pass  # Wood is static; fire handles ignition
```

---

### `update_stone(grid, x, y)`
Stone is inert. No physics.

```python
def update_stone(grid, x, y) -> None:
    pass
```

---

### `update_smoke(grid, x, y)`
Smoke rises and dissipates.

1. **Lifetime**: Smoke lives for 15–40 ticks (use `grid.fire_age` array reused for smoke age, or a separate `grid.gas_age` array)
2. **Rise**: Try `(x, y-1)` — if `EMPTY` → move up
3. Else try `(x-1, y-1)` or `(x+1, y-1)` randomly
4. Else try `(x-1, y)` or `(x+1, y)` randomly  
5. On each tick, 3% chance to just disappear (`EMPTY`) even without lifetime expiring

---

### `update_steam(grid, x, y)`
Steam behaves like smoke but rises faster and may condense back to water.

1. **Lifetime**: 30–80 ticks
2. **Rise**: Same as smoke but tries 2 cells up `(x, y-2)` first
3. **Condense**: 1% chance per tick to turn into `WATER` and fall

---

## Wiring into Grid

In `sand/grid.py`, import `physics` and update `_update_cell`:

```python
from sand import physics

def _update_cell(self, x: int, y: int) -> None:
    if self.updated[y][x]:
        return
    element = self.get(x, y)
    dispatch = {
        Element.SAND:  physics.update_sand,
        Element.WATER: physics.update_water,
        Element.FIRE:  physics.update_fire,
        Element.WOOD:  physics.update_wood,
        Element.STONE: physics.update_stone,
        Element.SMOKE: physics.update_smoke,
        Element.STEAM: physics.update_steam,
    }
    fn = dispatch.get(element)
    if fn:
        fn(self, x, y)
```

---

## Validation

Add a `if __name__ == "__main__"` block in `physics.py` that runs a headless simulation:

```python
if __name__ == "__main__":
    from sand.grid import Grid, Element
    g = Grid(20, 15)
    # Drop some sand
    for i in range(5, 15):
        g.set(i, 0, Element.SAND)
    # Pool of water
    for i in range(3, 12):
        g.set(i, 2, Element.WATER)
    # Wood plank
    for i in range(5, 15):
        g.set(i, 10, Element.WOOD)
    g.set(7, 9, Element.FIRE)

    for tick in range(100):
        g.tick()

    # Print final state as ASCII
    chars = {0:" ", 1:"S", 2:"~", 3:"F", 4:"W", 5:"#", 6:".", 7:"^"}
    for row in range(g.height):
        print("".join(chars.get(g.get(col, row), "?") for col in range(g.width)))
```

Expected: sand falls and piles, water spreads, fire burns wood and produces smoke.
