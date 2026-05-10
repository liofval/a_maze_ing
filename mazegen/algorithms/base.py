"""Abstract base class for maze generation algorithms.

All algorithms operate on a Maze that starts with all walls closed.
They carve passages by calling ``maze.remove_wall()``.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from collections.abc import Generator

from mazegen.maze import Maze


class MazeAlgorithm(ABC):
    """Strategy interface for maze generation algorithms.

    Implementations receive a fully-walled Maze and a seeded
    random.Random instance, and carve passages in place.
    """

    @abstractmethod
    def generate(self, maze: Maze, rng: random.Random) -> None:
        """Generate a perfect maze by carving passages.

        Parameters
        ----------
        maze : Maze
            A maze with all walls closed. Modified in place.
        rng : random.Random
            Seeded RNG for reproducible generation.
        """

    def generate_steps(
        self, maze: Maze, rng: random.Random
    ) -> Generator[tuple[int, int], None, None]:
        """Generate a maze, yielding (x, y) after each wall removal.

        The default implementation falls back to non-animated generation.
        Subclasses should override this to provide step-by-step output.

        Yields
        ------
        tuple[int, int]
            The (x, y) coordinates of the cell just carved into.
        """
        self.generate(maze, rng)
        return
        yield  # make this a generator
