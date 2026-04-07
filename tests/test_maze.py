"""Tests for the core maze data model."""

from mazegen.maze import Direction, Maze


class TestDirection:
    """Tests for Direction IntFlag."""

    def test_bit_values(self) -> None:
        assert int(Direction.N) == 1
        assert int(Direction.E) == 2
        assert int(Direction.S) == 4
        assert int(Direction.W) == 8

    def test_all_walls(self) -> None:
        assert int(Direction.all_walls()) == 0xF

    def test_to_char(self) -> None:
        assert Direction.N.to_char() == "N"
        assert Direction.E.to_char() == "E"
        assert Direction.S.to_char() == "S"
        assert Direction.W.to_char() == "W"

    def test_hex_encoding(self) -> None:
        walls = Direction.N | Direction.E  # 0011 = 3
        assert format(int(walls), "X") == "3"
        walls2 = Direction.E | Direction.W  # 1010 = A
        assert format(int(walls2), "X") == "A"


class TestMaze:
    """Tests for the Maze grid."""

    def test_initial_all_walls_closed(self) -> None:
        maze = Maze(5, 5, (0, 0), (4, 4))
        cell = maze.get_cell(2, 2)
        assert int(cell.walls) == 0xF

    def test_remove_wall_coherence(self) -> None:
        maze = Maze(5, 5, (0, 0), (4, 4))
        maze.remove_wall(2, 2, Direction.E)
        assert not maze.has_wall(2, 2, Direction.E)
        assert not maze.has_wall(3, 2, Direction.W)

    def test_remove_wall_preserves_others(self) -> None:
        maze = Maze(5, 5, (0, 0), (4, 4))
        maze.remove_wall(2, 2, Direction.E)
        assert maze.has_wall(2, 2, Direction.N)
        assert maze.has_wall(2, 2, Direction.S)
        assert maze.has_wall(2, 2, Direction.W)

    def test_add_wall_coherence(self) -> None:
        maze = Maze(5, 5, (0, 0), (4, 4))
        maze.remove_wall(2, 2, Direction.E)
        maze.add_wall(2, 2, Direction.E)
        assert maze.has_wall(2, 2, Direction.E)
        assert maze.has_wall(3, 2, Direction.W)

    def test_accessible_neighbors(self) -> None:
        maze = Maze(5, 5, (0, 0), (4, 4))
        assert maze.accessible_neighbors(2, 2) == []
        maze.remove_wall(2, 2, Direction.N)
        neighbors = maze.accessible_neighbors(2, 2)
        assert len(neighbors) == 1
        assert neighbors[0] == (2, 1, Direction.N)

    def test_boundary_check(self) -> None:
        maze = Maze(5, 5, (0, 0), (4, 4))
        assert maze.is_in_bounds(0, 0)
        assert maze.is_in_bounds(4, 4)
        assert not maze.is_in_bounds(-1, 0)
        assert not maze.is_in_bounds(5, 0)
