import random
from enum import IntEnum


class Element(IntEnum):
    EMPTY = 0
    SAND  = 1
    WATER = 2
    FIRE  = 3
    WOOD  = 4
    STONE = 5
    SMOKE = 6
    STEAM = 7


ELEMENT_META = {
    Element.EMPTY: {"char": " ",  "color_id": 0, "name": "Empty"},
    Element.SAND:  {"char": "█",  "color_id": 1, "name": "Sand"},
    Element.WATER: {"char": "~",  "color_id": 2, "name": "Water"},
    Element.FIRE:  {"char": "▲",  "color_id": 3, "name": "Fire"},
    Element.WOOD:  {"char": "#",  "color_id": 4, "name": "Wood"},
    Element.STONE: {"char": "▓",  "color_id": 5, "name": "Stone"},
    Element.SMOKE: {"char": "░",  "color_id": 6, "name": "Smoke"},
    Element.STEAM: {"char": "s",  "color_id": 7, "name": "Steam"},
}


class Grid:
    # Populated once on first tick; avoids recreating the dict per cell.
    _dispatch = None

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells   = [[Element.EMPTY] * width for _ in range(height)]
        self.updated = [[False] * width for _ in range(height)]
        self.fire_age = [[0] * width for _ in range(height)]
        self.gas_age  = [[0] * width for _ in range(height)]
        # Cells modified since the last render; None means full redraw needed.
        self.dirty: set | None = None

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x: int, y: int) -> Element:
        if not self.in_bounds(x, y):
            return Element.STONE
        return self.cells[y][x]

    def set(self, x: int, y: int, element: Element) -> None:
        if not self.in_bounds(x, y):
            return
        self.cells[y][x] = element
        if element == Element.FIRE:
            self.fire_age[y][x] = random.randint(20, 60)
        if self.dirty is not None:
            self.dirty.add((x, y))

    def clear(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.cells[y][x] = Element.EMPTY
        self.dirty = None  # signal full redraw

    def _swap(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.cells[y1][x1], self.cells[y2][x2] = self.cells[y2][x2], self.cells[y1][x1]
        self.updated[y1][x1] = True
        self.updated[y2][x2] = True
        if self.dirty is not None:
            self.dirty.add((x1, y1))
            self.dirty.add((x2, y2))

    def _update_cell(self, x: int, y: int) -> None:
        element = self.cells[y][x]
        if element == Element.EMPTY:
            return
        fn = Grid._dispatch.get(element)
        if fn:
            fn(self, x, y)

    def tick(self) -> None:
        if Grid._dispatch is None:
            from sand import physics
            Grid._dispatch = {
                Element.SAND:  physics.update_sand,
                Element.WATER: physics.update_water,
                Element.FIRE:  physics.update_fire,
                Element.WOOD:  physics.update_wood,
                Element.STONE: physics.update_stone,
                Element.SMOKE: physics.update_smoke,
                Element.STEAM: physics.update_steam,
            }

        if self.dirty is None:
            self.dirty = set()

        updated = self.updated
        for row in updated:
            for i in range(len(row)):
                row[i] = False

        cells = self.cells
        _update = self._update_cell
        for y in range(self.height - 1, -1, -1):
            row = cells[y]
            upd_row = updated[y]
            for x in range(self.width):
                if not upd_row[x] and row[x] != Element.EMPTY:
                    _update(x, y)


if __name__ == "__main__":
    grid = Grid(20, 10)
    grid.set(5,  0, Element.SAND)
    grid.set(10, 3, Element.WATER)
    grid.set(15, 5, Element.FIRE)
    grid.set(2,  7, Element.WOOD)
    grid.tick()

    for y in range(grid.height):
        row = ""
        for x in range(grid.width):
            elem = grid.get(x, y)
            row += ELEMENT_META[elem]["char"]
        print(row)
