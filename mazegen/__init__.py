"""mazegen - A reusable maze generation library.

Provides MazeGenerator as the main public API for generating
and solving mazes with multiple algorithm support.
"""

from mazegen.generator import MazeGenerator
from mazegen.maze import Cell, Direction, Maze

__all__ = ["MazeGenerator", "Maze", "Cell", "Direction"]
