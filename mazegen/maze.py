"""Core maze data model.

Defines Direction flags, Cell dataclass, and the Maze grid structure.
The Maze class enforces wall coherence: removing a wall from one cell
automatically removes the corresponding wall from its neighbor.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Direction(enum.IntFlag):
    """Cardinal directions as bit flags matching the output format.

    Bit 0 (LSB) = North, Bit 1 = East, Bit 2 = South, Bit 3 = West.
    A set bit means the wall is closed.

    Examples
    --------
    >>> Direction.N | Direction.S  # walls on north and south
    Direction.N|Direction.S
    >>> int(Direction.N | Direction.E)  # hex digit '3'
    3
    """

    N = 1   # 0001
    E = 2   # 0010
    S = 4   # 0100
    W = 8   # 1000

    @classmethod
    def all_walls(cls) -> Direction:
        """Return a bitmask with all four walls closed."""
        return cls.N | cls.E | cls.S | cls.W

    def to_char(self) -> str:
        """Convert a single direction to its letter representation.

        Returns
        -------
        str
            One of 'N', 'E', 'S', 'W'.

        Raises
        ------
        ValueError
            If the direction is not a single cardinal direction.
        """
        try:
            return _DIRECTION_CHARS[self]
        except KeyError:
            raise ValueError(
                f"{self!r} is not a single cardinal direction"
            ) from None


OPPOSITE: dict[Direction, Direction] = {
    Direction.N: Direction.S,
    Direction.S: Direction.N,
    Direction.E: Direction.W,
    Direction.W: Direction.E,
}

DIRECTION_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.N: (0, -1),
    Direction.E: (1, 0),
    Direction.S: (0, 1),
    Direction.W: (-1, 0),
}

_DIRECTION_CHARS: dict[Direction, str] = {
    Direction.N: "N",
    Direction.E: "E",
    Direction.S: "S",
    Direction.W: "W",
}

ALL_DIRECTIONS: list[Direction] = [
    Direction.N, Direction.E, Direction.S, Direction.W,
]


@dataclass
class Cell:
    """A single cell in the maze grid.

    Attributes
    ----------
    x : int
        Column index (0-based, left to right).
    y : int
        Row index (0-based, top to bottom).
    walls : Direction
        Bitmask of closed walls. Default: all four walls closed (0xF).
    """

    x: int
    y: int
    walls: Direction = field(default_factory=Direction.all_walls)


class Maze:
    """A 2D grid of cells representing a maze.

    The grid is initialized with all walls closed. Use ``remove_wall``
    to carve passages; it automatically maintains wall coherence
    between neighboring cells.

    Parameters
    ----------
    width : int
        Number of columns (cells).
    height : int
        Number of rows (cells).
    entry : tuple[int, int]
        Entry coordinates (x, y).
    exit_ : tuple[int, int]
        Exit coordinates (x, y).
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> None:
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_ = exit_
        self.pattern_cells: set[tuple[int, int]] = set()
        self._grid: list[list[Cell]] = [
            [Cell(x=x, y=y) for x in range(width)]
            for y in range(height)
        ]

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Check if coordinates are within the maze boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at (x, y).

        Raises
        ------
        IndexError
            If coordinates are out of bounds.
        """
        if not self.is_in_bounds(x, y):
            raise IndexError(f"Cell ({x}, {y}) is out of bounds")
        return self._grid[y][x]

    def has_wall(self, x: int, y: int, direction: Direction) -> bool:
        """Check if the cell at (x, y) has a wall in the given direction."""
        return bool(self.get_cell(x, y).walls & direction)

    def remove_wall(self, x: int, y: int, direction: Direction) -> None:
        """Remove a wall from (x, y) and the matching wall from the neighbor.

        This is the only method that should be used to modify walls,
        ensuring coherence between adjacent cells.

        Parameters
        ----------
        x : int
            Column of the cell.
        y : int
            Row of the cell.
        direction : Direction
            Which wall to remove (must be a single direction).

        Raises
        ------
        IndexError
            If the cell or its neighbor is out of bounds.
        """
        cell = self.get_cell(x, y)
        cell.walls &= ~direction

        dx, dy = DIRECTION_DELTA[direction]
        nx, ny = x + dx, y + dy
        if self.is_in_bounds(nx, ny):
            neighbor = self.get_cell(nx, ny)
            neighbor.walls &= ~OPPOSITE[direction]

    def add_wall(self, x: int, y: int, direction: Direction) -> None:
        """Add a wall to (x, y) and the matching wall to the neighbor.

        Maintains wall coherence, like ``remove_wall``.

        Parameters
        ----------
        x : int
            Column of the cell.
        y : int
            Row of the cell.
        direction : Direction
            Which wall to add (must be a single direction).
        """
        cell = self.get_cell(x, y)
        cell.walls |= direction

        dx, dy = DIRECTION_DELTA[direction]
        nx, ny = x + dx, y + dy
        if self.is_in_bounds(nx, ny):
            neighbor = self.get_cell(nx, ny)
            neighbor.walls |= OPPOSITE[direction]

    def close_all_walls(self, x: int, y: int) -> None:
        """Set all four walls of cell (x, y) and update neighbors."""
        for d in ALL_DIRECTIONS:
            self.add_wall(x, y, d)

    def neighbors(
        self, x: int, y: int
    ) -> list[tuple[int, int, Direction]]:
        """Return in-bounds neighbors as (nx, ny, direction) tuples."""
        result: list[tuple[int, int, Direction]] = []
        for d in ALL_DIRECTIONS:
            dx, dy = DIRECTION_DELTA[d]
            nx, ny = x + dx, y + dy
            if self.is_in_bounds(nx, ny):
                result.append((nx, ny, d))
        return result

    def accessible_neighbors(
        self, x: int, y: int
    ) -> list[tuple[int, int, Direction]]:
        """Return neighbors reachable through open walls."""
        return [
            (nx, ny, d)
            for nx, ny, d in self.neighbors(x, y)
            if not self.has_wall(x, y, d)
        ]

    def iter_cells(self) -> list[Cell]:
        """Return a flat list of all cells, row by row."""
        return [cell for row in self._grid for cell in row]

    def row(self, y: int) -> list[Cell]:
        """Return all cells in the given row."""
        return list(self._grid[y])
