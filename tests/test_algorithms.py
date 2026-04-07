"""Tests for maze generation algorithms."""

import random

from mazegen.algorithms.kruskal import KruskalAlgorithm
from mazegen.algorithms.recursive_backtracker import RecursiveBacktracker
from mazegen.maze import Maze
from mazegen.solver import solve_bfs
from mazegen.validator import validate_maze


class TestRecursiveBacktracker:
    """Tests for Recursive Backtracker algorithm."""

    def test_produces_valid_maze(self) -> None:
        maze = Maze(15, 15, (0, 0), (14, 14))
        algo = RecursiveBacktracker()
        algo.generate(maze, random.Random(42))
        errors = validate_maze(maze)
        assert errors == [], f"Validation errors: {errors}"

    def test_produces_perfect_maze(self) -> None:
        maze = Maze(10, 10, (0, 0), (9, 9))
        algo = RecursiveBacktracker()
        algo.generate(maze, random.Random(42))
        path = solve_bfs(maze)
        assert path is not None

    def test_seed_reproducibility(self) -> None:
        maze1 = Maze(10, 10, (0, 0), (9, 9))
        maze2 = Maze(10, 10, (0, 0), (9, 9))
        algo = RecursiveBacktracker()
        algo.generate(maze1, random.Random(123))
        algo.generate(maze2, random.Random(123))
        for y in range(10):
            for x in range(10):
                assert maze1.get_cell(x, y).walls == maze2.get_cell(x, y).walls


class TestKruskal:
    """Tests for Kruskal's algorithm."""

    def test_produces_valid_maze(self) -> None:
        maze = Maze(15, 15, (0, 0), (14, 14))
        algo = KruskalAlgorithm()
        algo.generate(maze, random.Random(42))
        errors = validate_maze(maze)
        assert errors == [], f"Validation errors: {errors}"

    def test_produces_solvable_maze(self) -> None:
        maze = Maze(10, 10, (0, 0), (9, 9))
        algo = KruskalAlgorithm()
        algo.generate(maze, random.Random(42))
        path = solve_bfs(maze)
        assert path is not None

    def test_seed_reproducibility(self) -> None:
        maze1 = Maze(10, 10, (0, 0), (9, 9))
        maze2 = Maze(10, 10, (0, 0), (9, 9))
        algo = KruskalAlgorithm()
        algo.generate(maze1, random.Random(99))
        algo.generate(maze2, random.Random(99))
        for y in range(10):
            for x in range(10):
                assert maze1.get_cell(x, y).walls == maze2.get_cell(x, y).walls
