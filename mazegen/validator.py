"""Maze validation.

Checks structural correctness: wall coherence, connectivity,
corridor width, entry/exit placement, and border walls.
"""

from __future__ import annotations

from collections import deque

from mazegen.maze import (
    ALL_DIRECTIONS,
    DIRECTION_DELTA,
    OPPOSITE,
    Direction,
    Maze,
)


def validate_maze(maze: Maze) -> list[str]:
    """Run all validation checks and return a list of error messages.

    Parameters
    ----------
    maze : Maze
        The maze to validate.

    Returns
    -------
    list[str]
        Error messages. Empty list means the maze is valid.
    """
    errors: list[str] = []
    errors.extend(_check_entry_exit(maze))
    errors.extend(_check_wall_coherence(maze))
    errors.extend(_check_connectivity(maze))
    errors.extend(_check_no_large_open_areas(maze))
    errors.extend(_check_border_walls(maze))
    return errors


def _check_entry_exit(maze: Maze) -> list[str]:
    """Validate entry and exit coordinates."""
    errors: list[str] = []
    ex, ey = maze.entry
    xx, xy = maze.exit_

    if not maze.is_in_bounds(ex, ey):
        errors.append(f"Entry ({ex},{ey}) is out of bounds")
    if not maze.is_in_bounds(xx, xy):
        errors.append(f"Exit ({xx},{xy}) is out of bounds")
    if maze.entry == maze.exit_:
        errors.append("Entry and exit must be different")

    return errors


def _check_wall_coherence(maze: Maze) -> list[str]:
    """Verify that adjacent cells agree on shared walls."""
    errors: list[str] = []
    for y in range(maze.height):
        for x in range(maze.width):
            for d in ALL_DIRECTIONS:
                dx, dy = DIRECTION_DELTA[d]
                nx, ny = x + dx, y + dy
                if not maze.is_in_bounds(nx, ny):
                    continue
                has_wall_here = maze.has_wall(x, y, d)
                has_wall_there = maze.has_wall(nx, ny, OPPOSITE[d])
                if has_wall_here != has_wall_there:
                    errors.append(
                        f"Wall incoherence at ({x},{y}){d.to_char()} "
                        f"vs ({nx},{ny}){OPPOSITE[d].to_char()}"
                    )
    return errors


def _check_connectivity(maze: Maze) -> list[str]:
    """Verify all non-pattern cells are reachable from the entry."""
    pattern = maze.pattern_cells
    all_cells = {
        (c.x, c.y) for c in maze.iter_cells()
        if (c.x, c.y) not in pattern
    }

    if not all_cells:
        return []

    start = maze.entry
    if start in pattern:
        return ["Entry is inside the 42 pattern"]

    visited: set[tuple[int, int]] = {start}
    queue: deque[tuple[int, int]] = deque([start])

    while queue:
        cx, cy = queue.popleft()
        for nx, ny, _d in maze.accessible_neighbors(cx, cy):
            if (nx, ny) not in visited and (nx, ny) not in pattern:
                visited.add((nx, ny))
                queue.append((nx, ny))

    unreachable = all_cells - visited
    if unreachable:
        sample = list(unreachable)[:5]
        return [
            f"{len(unreachable)} cells unreachable from entry. "
            f"Examples: {sample}"
        ]
    return []


def _check_no_large_open_areas(maze: Maze) -> list[str]:
    """Verify no 3x3 block of cells has all internal walls removed."""
    errors: list[str] = []
    for y in range(maze.height - 2):
        for x in range(maze.width - 2):
            if is_3x3_open(maze, x, y):
                errors.append(
                    f"3x3 open area detected at ({x},{y})"
                )
    return errors


def is_3x3_open(maze: Maze, x: int, y: int) -> bool:
    """Check if the 3x3 block starting at (x, y) has no internal walls."""
    for dy in range(3):
        for dx in range(3):
            cx, cy = x + dx, y + dy
            if dx < 2 and maze.has_wall(cx, cy, Direction.E):
                return False
            if dy < 2 and maze.has_wall(cx, cy, Direction.S):
                return False
    return True


def _check_border_walls(maze: Maze) -> list[str]:
    """Verify that border cells have walls on the maze boundary."""
    errors: list[str] = []
    for x in range(maze.width):
        if not maze.has_wall(x, 0, Direction.N):
            errors.append(f"Missing north border wall at ({x},0)")
        if not maze.has_wall(x, maze.height - 1, Direction.S):
            errors.append(
                f"Missing south border wall at ({x},{maze.height - 1})"
            )
    for y in range(maze.height):
        if not maze.has_wall(0, y, Direction.W):
            errors.append(f"Missing west border wall at (0,{y})")
        if not maze.has_wall(maze.width - 1, y, Direction.E):
            errors.append(
                f"Missing east border wall at ({maze.width - 1},{y})"
            )
    return errors
