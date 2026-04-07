"""Abstract base class for maze generation algorithms.

All algorithms operate on a Maze that starts with all walls closed.
They carve passages by calling ``maze.remove_wall()``.
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod

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
