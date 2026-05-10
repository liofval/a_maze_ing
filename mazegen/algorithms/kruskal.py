"""Kruskal's algorithm for maze generation.

Uses a Union-Find (disjoint set) data structure to produce
a perfect maze with a more branchy, balanced feel compared
to the Recursive Backtracker.
"""

from __future__ import annotations

import random
from collections.abc import Generator

from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import ALL_DIRECTIONS, DIRECTION_DELTA, Maze


class _UnionFind:
    """Disjoint set data structure with union by rank and path compression."""

    def __init__(self, size: int) -> None:
        self._parent = list(range(size))
        self._rank = [0] * size

    def find(self, x: int) -> int:
        """Find the root of x with path compression."""
        while self._parent[x] != x:
            self._parent[x] = self._parent[self._parent[x]]
            x = self._parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        """Merge sets containing a and b. Return True if they were separate."""
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self._rank[ra] < self._rank[rb]:
            ra, rb = rb, ra
        self._parent[rb] = ra
        if self._rank[ra] == self._rank[rb]:
            self._rank[ra] += 1
        return True


class KruskalAlgorithm(MazeAlgorithm):
    """Generate a perfect maze using Kruskal's algorithm.

    Algorithm
    ---------
    1. List all internal walls (edges between adjacent cells).
    2. Shuffle them randomly.
    3. For each wall: if it separates two different sets, remove it
       and union the sets.
    4. Stop when all cells are in one connected component.
    """

    def _run(
        self, maze: Maze, rng: random.Random
    ) -> Generator[tuple[int, int], None, None]:
        """Core Kruskal logic as a generator, yielding each carved cell."""
        uf = _UnionFind(maze.width * maze.height)

        frozen = maze.pattern_cells
        walls: list[tuple[int, int, int, int, int]] = []
        for y in range(maze.height):
            for x in range(maze.width):
                if (x, y) in frozen:
                    continue
                for d in ALL_DIRECTIONS:
                    dx, dy = DIRECTION_DELTA[d]
                    nx, ny = x + dx, y + dy
                    if (
                        maze.is_in_bounds(nx, ny)
                        and (nx, ny) not in frozen
                        and (nx > x or (nx == x and ny > y))
                    ):
                        walls.append((x, y, nx, ny, int(d)))

        rng.shuffle(walls)

        for x1, y1, x2, y2, d_int in walls:
            idx1 = y1 * maze.width + x1
            idx2 = y2 * maze.width + x2
            if uf.union(idx1, idx2):
                from mazegen.maze import Direction
                maze.remove_wall(x1, y1, Direction(d_int))
                yield (x2, y2)

    def generate(self, maze: Maze, rng: random.Random) -> None:
        """Carve a perfect maze using randomized Kruskal's."""
        for _ in self._run(maze, rng):
            pass

    def generate_steps(
        self, maze: Maze, rng: random.Random
    ) -> Generator[tuple[int, int], None, None]:
        """Carve a maze step by step, yielding each carved cell."""
        yield from self._run(maze, rng)
