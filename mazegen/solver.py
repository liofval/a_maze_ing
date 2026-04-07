"""BFS-based shortest path solver for mazes.

Guarantees the shortest path in an unweighted grid.
For perfect mazes, this is the only path.
"""

from __future__ import annotations

from collections import deque

from mazegen.maze import Direction, Maze


def solve_bfs(maze: Maze) -> list[Direction] | None:
    """Find the shortest path from entry to exit using BFS.

    Parameters
    ----------
    maze : Maze
        The maze to solve.

    Returns
    -------
    list[Direction] | None
        Sequence of directions from entry to exit,
        or None if no path exists.
    """
    start = maze.entry
    goal = maze.exit_

    if start == goal:
        return []

    visited: set[tuple[int, int]] = {start}
    parent: dict[tuple[int, int], tuple[tuple[int, int], Direction]] = {}
    queue: deque[tuple[int, int]] = deque([start])

    while queue:
        cx, cy = queue.popleft()

        for nx, ny, d in maze.accessible_neighbors(cx, cy):
            if (nx, ny) in visited:
                continue
            visited.add((nx, ny))
            parent[(nx, ny)] = ((cx, cy), d)

            if (nx, ny) == goal:
                return _reconstruct_path(parent, start, goal)

            queue.append((nx, ny))

    return None


def _reconstruct_path(
    parent: dict[tuple[int, int], tuple[tuple[int, int], Direction]],
    start: tuple[int, int],
    goal: tuple[int, int],
) -> list[Direction]:
    """Trace back from goal to start and return the path as directions."""
    path: list[Direction] = []
    current = goal
    while current != start:
        prev, direction = parent[current]
        path.append(direction)
        current = prev
    path.reverse()
    return path


def path_to_string(path: list[Direction]) -> str:
    """Convert a direction path to a string of N/E/S/W characters.

    Parameters
    ----------
    path : list[Direction]
        Sequence of single directions.

    Returns
    -------
    str
        Concatenated direction characters, e.g. 'SSENNW'.
    """
    return "".join(d.to_char() for d in path)
