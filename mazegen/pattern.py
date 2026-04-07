"""Stamp a visible '42' pattern into a maze using fully closed cells.

The pattern is placed BEFORE maze generation. Pattern cells are
marked with all walls closed and added to maze.pattern_cells.
The generation algorithm then routes around them.
"""

from __future__ import annotations

import random

from mazegen.maze import Maze

# Bitmap for "4": 5 rows x 3 cols
_PATTERN_4: list[tuple[int, int]] = [
    (0, 0),         (2, 0),
    (0, 1),         (2, 1),
    (0, 2), (1, 2), (2, 2),
                    (2, 3),
                    (2, 4),
]

# Bitmap for "2": 5 rows x 3 cols
_PATTERN_2: list[tuple[int, int]] = [
    (0, 0), (1, 0), (2, 0),
                    (2, 1),
    (0, 2), (1, 2), (2, 2),
    (0, 3),
    (0, 4), (1, 4), (2, 4),
]

PATTERN_HEIGHT = 5
PATTERN_4_WIDTH = 3
PATTERN_2_WIDTH = 3
GAP = 1
TOTAL_WIDTH = PATTERN_4_WIDTH + GAP + PATTERN_2_WIDTH  # 7
TOTAL_HEIGHT = PATTERN_HEIGHT  # 5

MIN_MAZE_WIDTH = TOTAL_WIDTH + 4   # 11
MIN_MAZE_HEIGHT = TOTAL_HEIGHT + 4  # 9


def can_stamp(maze: Maze) -> bool:
    """Check if the maze is large enough for the 42 pattern."""
    return maze.width >= MIN_MAZE_WIDTH and maze.height >= MIN_MAZE_HEIGHT


def stamp_42(maze: Maze, rng: random.Random) -> bool:
    """Stamp the '42' pattern into the maze before generation.

    Marks pattern cells with all walls closed and adds them
    to maze.pattern_cells. The generation algorithm must skip
    these cells.

    Parameters
    ----------
    maze : Maze
        The maze (all walls still closed, before generation).
    rng : random.Random
        Seeded RNG for position selection.

    Returns
    -------
    bool
        True if the pattern was successfully placed.
    """
    if not can_stamp(maze):
        return False

    margin = 2
    x_min = margin
    x_max = maze.width - TOTAL_WIDTH - margin
    y_min = margin
    y_max = maze.height - TOTAL_HEIGHT - margin

    if x_max < x_min or y_max < y_min:
        return False

    positions = [
        (x, y)
        for x in range(x_min, x_max + 1)
        for y in range(y_min, y_max + 1)
    ]
    rng.shuffle(positions)

    ex, ey = maze.entry
    xx, xy = maze.exit_

    for ox, oy in positions:
        cells = _pattern_cells(ox, oy)

        if (ex, ey) in cells or (xx, xy) in cells:
            continue

        # Pattern cells keep all walls closed (already the default).
        # Just register them so the algorithm skips them.
        maze.pattern_cells = cells
        return True

    return False


def _pattern_cells(
    ox: int, oy: int
) -> set[tuple[int, int]]:
    """Compute absolute cell positions for the '42' pattern."""
    cells: set[tuple[int, int]] = set()
    for dx, dy in _PATTERN_4:
        cells.add((ox + dx, oy + dy))
    offset_x = PATTERN_4_WIDTH + GAP
    for dx, dy in _PATTERN_2:
        cells.add((ox + offset_x + dx, oy + dy))
    return cells
