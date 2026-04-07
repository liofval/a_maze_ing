"""Tests for the BFS maze solver."""

import random

from mazegen.algorithms.recursive_backtracker import RecursiveBacktracker
from mazegen.maze import Direction, Maze
from mazegen.solver import path_to_string, solve_bfs


class TestSolveBfs:
    """Tests for BFS solver."""

    def test_simple_path(self) -> None:
        maze = Maze(3, 1, (0, 0), (2, 0))
        maze.remove_wall(0, 0, Direction.E)
        maze.remove_wall(1, 0, Direction.E)
        path = solve_bfs(maze)
        assert path == [Direction.E, Direction.E]

    def test_no_path(self) -> None:
        maze = Maze(3, 3, (0, 0), (2, 2))
        # All walls closed -> no path
        path = solve_bfs(maze)
        assert path is None

    def test_path_on_generated_maze(self) -> None:
        maze = Maze(20, 15, (0, 0), (19, 14))
        algo = RecursiveBacktracker()
        algo.generate(maze, random.Random(42))
        path = solve_bfs(maze)
        assert path is not None
        assert len(path) > 0


class TestPathToString:
    """Tests for path-to-string conversion."""

    def test_conversion(self) -> None:
        path = [Direction.S, Direction.E, Direction.N, Direction.W]
        assert path_to_string(path) == "SENW"

    def test_empty(self) -> None:
        assert path_to_string([]) == ""
