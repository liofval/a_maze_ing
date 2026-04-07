"""Recursive Backtracker (iterative DFS) maze generation.

Produces long, winding corridors. Uses an explicit stack
instead of Python recursion to avoid stack overflow on large mazes.
"""

from __future__ import annotations

import random

from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Maze


class RecursiveBacktracker(MazeAlgorithm):
    """Generate a perfect maze using iterative depth-first search.

    Algorithm
    ---------
    1. Start from entry cell, push onto stack, mark visited.
    2. While stack is not empty:
       a. Peek at top cell.
       b. Find unvisited neighbors.
       c. If any: pick one at random, remove wall, push, mark.
       d. If none: pop (backtrack).
    """

    def generate(self, maze: Maze, rng: random.Random) -> None:
        """Carve a perfect maze using iterative DFS.

        Parameters
        ----------
        maze : Maze
            Fully-walled maze to carve. Modified in place.
        rng : random.Random
            Seeded RNG for reproducible results.
        """
        visited: set[tuple[int, int]] = set()
        stack: list[tuple[int, int]] = []

        sx, sy = maze.entry
        visited.add((sx, sy))
        stack.append((sx, sy))

        while stack:
            cx, cy = stack[-1]

            frozen = maze.pattern_cells
            unvisited = [
                (nx, ny, d)
                for nx, ny, d in maze.neighbors(cx, cy)
                if (nx, ny) not in visited and (nx, ny) not in frozen
            ]

            if unvisited:
                nx, ny, direction = rng.choice(unvisited)
                maze.remove_wall(cx, cy, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
