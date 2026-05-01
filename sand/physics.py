import random
from sand.grid import Grid, Element


def update_sand(grid: Grid, x: int, y: int) -> None:
    _passable = (Element.EMPTY, Element.WATER)
    if grid.get(x, y + 1) in _passable:
        grid._swap(x, y, x, y + 1)
        return
    dirs = [-1, 1]
    random.shuffle(dirs)
    for dx in dirs:
        if grid.get(x + dx, y + 1) in _passable:
            grid._swap(x, y, x + dx, y + 1)
            return


def update_water(grid: Grid, x: int, y: int) -> None:
    if grid.get(x, y + 1) == Element.EMPTY:
        grid._swap(x, y, x, y + 1)
        return
    dirs = [-1, 1]
    random.shuffle(dirs)
    for dx in dirs:
        if grid.get(x + dx, y) == Element.EMPTY:
            grid._swap(x, y, x + dx, y)
            return


def update_fire(grid: Grid, x: int, y: int) -> None:
    grid.fire_age[y][x] -= 1
    if grid.fire_age[y][x] <= 0:
        grid.cells[y][x] = Element.SMOKE if random.random() < 0.5 else Element.EMPTY
        grid.gas_age[y][x] = random.randint(15, 40)
        grid.updated[y][x] = True
        return

    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if not grid.in_bounds(nx, ny):
            continue
        neighbor = grid.get(nx, ny)
        if neighbor == Element.WOOD and random.random() < 0.05:
            grid.cells[ny][nx] = Element.FIRE
            grid.fire_age[ny][nx] = random.randint(20, 60)
            grid.updated[ny][nx] = True
        elif neighbor == Element.WATER and random.random() < 0.30:
            grid.cells[ny][nx] = Element.STEAM
            grid.gas_age[ny][nx] = random.randint(30, 80)
            grid.updated[ny][nx] = True
            grid.cells[y][x] = Element.EMPTY
            grid.updated[y][x] = True
            return


def update_wood(grid: Grid, x: int, y: int) -> None:
    pass


def update_stone(grid: Grid, x: int, y: int) -> None:
    pass


def _rise(grid: Grid, x: int, y: int, age_array, extra_up: bool = False) -> bool:
    """Try to move a gas cell upward. Returns True if it moved."""
    candidates = []
    if extra_up and grid.get(x, y - 2) == Element.EMPTY:
        candidates.append((x, y - 2))
    if grid.get(x, y - 1) == Element.EMPTY:
        candidates.append((x, y - 1))
    if not candidates:
        diags = [(x - 1, y - 1), (x + 1, y - 1)]
        random.shuffle(diags)
        for nx, ny in diags:
            if grid.get(nx, ny) == Element.EMPTY:
                candidates.append((nx, ny))
    if not candidates:
        sides = [(x - 1, y), (x + 1, y)]
        random.shuffle(sides)
        for nx, ny in sides:
            if grid.get(nx, ny) == Element.EMPTY:
                candidates.append((nx, ny))
    if candidates:
        nx, ny = candidates[0]
        age_array[ny][nx] = age_array[y][x]
        grid._swap(x, y, nx, ny)
        return True
    return False


def update_smoke(grid: Grid, x: int, y: int) -> None:
    grid.gas_age[y][x] -= 1
    if grid.gas_age[y][x] <= 0 or random.random() < 0.03:
        grid.cells[y][x] = Element.EMPTY
        grid.updated[y][x] = True
        return
    _rise(grid, x, y, grid.gas_age)


def update_steam(grid: Grid, x: int, y: int) -> None:
    grid.gas_age[y][x] -= 1
    if grid.gas_age[y][x] <= 0:
        grid.cells[y][x] = Element.EMPTY
        grid.updated[y][x] = True
        return
    if random.random() < 0.01:
        grid.cells[y][x] = Element.WATER
        grid.updated[y][x] = True
        return
    _rise(grid, x, y, grid.gas_age, extra_up=True)


if __name__ == "__main__":
    from sand.grid import Grid, Element
    g = Grid(20, 15)
    for i in range(5, 15):
        g.set(i, 0, Element.SAND)
    for i in range(3, 12):
        g.set(i, 2, Element.WATER)
    for i in range(5, 15):
        g.set(i, 10, Element.WOOD)
    g.set(7, 9, Element.FIRE)

    for tick in range(100):
        g.tick()

    chars = {0: " ", 1: "S", 2: "~", 3: "F", 4: "W", 5: "#", 6: ".", 7: "^"}
    for row in range(g.height):
        print("".join(chars.get(g.get(col, row), "?") for col in range(g.width)))
