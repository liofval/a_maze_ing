"""MazeGenerator - the public facade for maze generation.

This is the main class users of the mazegen library interact with.

Example
-------
>>> from mazegen import MazeGenerator
>>> gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit_=(19, 14))
>>> maze = gen.generate()
>>> path = gen.solve()
"""

from __future__ import annotations

import random
import sys
from collections.abc import Generator

from mazegen.algorithms import ALGORITHMS
from mazegen.algorithms.base import MazeAlgorithm
from mazegen.maze import Direction, Maze
from mazegen.pattern import can_stamp, stamp_42
from mazegen.solver import solve_bfs
from mazegen.validator import is_3x3_open, validate_maze


class MazeGenerator:
    """Facade for generating, validating, and solving mazes.

    Parameters
    ----------
    width : int
        Number of columns.
    height : int
        Number of rows.
    entry : tuple[int, int]
        Entry coordinates (x, y).
    exit_ : tuple[int, int]
        Exit coordinates (x, y).
    perfect : bool
        If True, generate a perfect maze (exactly one path).
    seed : int | None
        Random seed for reproducibility. None = random.
    algorithm : str
        Name of the generation algorithm (see ALGORITHMS registry).
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        perfect: bool = True,
        seed: int | None = None,
        algorithm: str = "recursive_backtracker",
    ) -> None:
        # --- Input validation ---
        if not isinstance(width, int) or not isinstance(height, int):
            raise TypeError("width and height must be integers")
        if width <= 0 or height <= 0:
            raise ValueError(
                f"width and height must be positive, got: {width}x{height}"
            )
        MAX_SIZE = 1000
        if width > MAX_SIZE or height > MAX_SIZE:
            raise ValueError(
                f"width and height must be at most {MAX_SIZE}, "
                f"got: {width}x{height}"
            )
        if width == 1 and height == 1:
            raise ValueError(
                "Maze too small: a 1x1 maze cannot have distinct "
                "entry and exit"
            )

        ex, ey = entry
        xx, xy = exit_
        if not (0 <= ex < width and 0 <= ey < height):
            raise ValueError(
                f"Entry ({ex},{ey}) is out of bounds "
                f"for a {width}x{height} maze"
            )
        if not (0 <= xx < width and 0 <= xy < height):
            raise ValueError(
                f"Exit ({xx},{xy}) is out of bounds "
                f"for a {width}x{height} maze"
            )
        if entry == exit_:
            raise ValueError("Entry and exit must be different")

        if algorithm not in ALGORITHMS:
            available = ", ".join(sorted(ALGORITHMS.keys()))
            raise ValueError(
                f"Unknown algorithm '{algorithm}'. "
                f"Available: {available}"
            )

        self._width = width
        self._height = height
        self._entry = entry
        self._exit = exit_
        self._perfect = perfect
        self._seed = seed
        self._algorithm_name = algorithm
        self._maze: Maze | None = None
        self._solution: list[Direction] | None = None

    def generate(self) -> Maze:
        """Generate a new maze and return it.

        Returns
        -------
        Maze
            The generated maze.

        Raises
        ------
        RuntimeError
            If the generated maze fails validation.
        """
        rng = random.Random(self._seed)

        maze = Maze(
            self._width, self._height,
            self._entry, self._exit,
        )

        # Stamp '42' pattern BEFORE generation so the algorithm
        # routes around the frozen cells.
        if can_stamp(maze):
            if not stamp_42(maze, rng):
                print(
                    "Warning: Could not place '42' pattern",
                    file=sys.stderr,
                )
        else:
            print(
                "Warning: Maze too small for '42' pattern",
                file=sys.stderr,
            )

        algo: MazeAlgorithm = ALGORITHMS[self._algorithm_name]()
        algo.generate(maze, rng)

        if not self._perfect:
            self._make_imperfect(maze, rng)

        errors = validate_maze(maze)
        if errors:
            raise RuntimeError(
                "Maze validation failed:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

        self._maze = maze
        self._solution = None
        return maze

    def solve(self) -> list[Direction] | None:
        """Find the shortest path from entry to exit.

        Returns
        -------
        list[Direction] | None
            The path as a list of directions, or None if no path.

        Raises
        ------
        RuntimeError
            If no maze has been generated yet.
        """
        if self._maze is None:
            raise RuntimeError("No maze generated yet. Call generate() first.")
        self._solution = solve_bfs(self._maze)
        return self._solution

    def generate_animated(self) -> Generator[tuple[Maze, int, int], None, None]:
        """Generate a maze step by step for animation.

        Yields
        ------
        tuple[Maze, int, int]
            The maze and the (x, y) of the cell just carved.
        """
        rng = random.Random(self._seed)

        maze = Maze(
            self._width, self._height,
            self._entry, self._exit,
        )

        if can_stamp(maze):
            if not stamp_42(maze, rng):
                print(
                    "Warning: Could not place '42' pattern",
                    file=sys.stderr,
                )
        else:
            print(
                "Warning: Maze too small for '42' pattern",
                file=sys.stderr,
            )

        algo: MazeAlgorithm = ALGORITHMS[self._algorithm_name]()
        for x, y in algo.generate_steps(maze, rng):
            yield (maze, x, y)

        if not self._perfect:
            self._make_imperfect(maze, rng)

        self._maze = maze
        self._solution = None

    def get_maze(self) -> Maze:
        """Return the last generated maze.

        Raises
        ------
        RuntimeError
            If no maze has been generated yet.
        """
        if self._maze is None:
            raise RuntimeError("No maze generated yet. Call generate() first.")
        return self._maze

    def _make_imperfect(
        self, maze: Maze, rng: random.Random
    ) -> None:
        """Remove extra walls to create loops in the maze.

        Removes approximately 5-10% of remaining walls,
        respecting the 'no 3x3 open area' constraint.
        """
        candidates: list[tuple[int, int, Direction]] = []
        for y in range(maze.height):
            for x in range(maze.width):
                for nx, ny, d in maze.neighbors(x, y):
                    if maze.has_wall(x, y, d):
                        candidates.append((x, y, d))

        rng.shuffle(candidates)
        target = max(1, len(candidates) // 15)
        removed = 0

        for x, y, d in candidates:
            if removed >= target:
                break
            if not maze.has_wall(x, y, d):
                continue
            maze.remove_wall(x, y, d)
            if self._has_3x3_near(maze, x, y):
                maze.add_wall(x, y, d)
            else:
                removed += 1

    @staticmethod
    def _has_3x3_near(maze: Maze, x: int, y: int) -> bool:
        """Check if any 3x3 open area exists near (x, y)."""
        for sy in range(max(0, y - 2), min(maze.height - 2, y + 1)):
            for sx in range(max(0, x - 2), min(maze.width - 2, x + 1)):
                if is_3x3_open(maze, sx, sy):
                    return True
        return False
