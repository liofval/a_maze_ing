"""Maze generation algorithms with a registry for easy extensibility.

To add a new algorithm:
1. Create a class inheriting from ``MazeAlgorithm`` in this package.
2. Register it in the ``ALGORITHMS`` dict below.
"""

from __future__ import annotations

from mazegen.algorithms.base import MazeAlgorithm
from mazegen.algorithms.kruskal import KruskalAlgorithm
from mazegen.algorithms.recursive_backtracker import RecursiveBacktracker

ALGORITHMS: dict[str, type[MazeAlgorithm]] = {
    "recursive_backtracker": RecursiveBacktracker,
    "kruskal": KruskalAlgorithm,
}

__all__ = ["MazeAlgorithm", "ALGORITHMS"]
