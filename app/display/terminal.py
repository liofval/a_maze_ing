"""ASCII terminal renderer for mazes.

Each cell is rendered as a 2-character-wide block with walls
drawn using box-drawing-like characters. Entry, exit, path,
and the '42' pattern are color-coded.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Generator

from mazegen.maze import DIRECTION_DELTA, Direction, Maze
from app.display.base import MazeDisplay
from app.display.colors import ColorScheme, SCHEMES


class TerminalDisplay(MazeDisplay):
    """Render mazes to the terminal using ASCII art and ANSI colors.

    Each cell occupies a 2x1 character area in the output grid,
    with walls represented as lines between cells.
    The top-left corner is (0, 0).

    Rendering Layout (for each cell)
    --------------------------------
    ::

        +--+
        |  |
        +--+

    Adjacent cells share walls, so the full grid is
    (2*width + 1) columns by (2*height + 1) rows.
    """

    def __init__(self) -> None:
        self._color_index: int = 0

    @property
    def color_scheme(self) -> ColorScheme:
        """Return the current color scheme."""
        return SCHEMES[self._color_index % len(SCHEMES)]

    def cycle_colors(self) -> None:
        """Switch to the next color scheme."""
        self._color_index += 1

    def render(
        self,
        maze: Maze,
        show_path: bool = False,
        solution: list[Direction] | None = None,
    ) -> None:
        """Render the maze to stdout.

        Parameters
        ----------
        maze : Maze
            The maze to render.
        show_path : bool
            Whether to show the solution path.
        solution : list[Direction] | None
            The solution path directions.
        """
        print(self._build_grid_string(maze, show_path, solution))


    def render_animated(
        self,
        steps: Generator[tuple[Maze, int, int], None, None],
        delay: float = 0.03,
    ) -> Maze:
        """Render maze generation as an animation.

        Parameters
        ----------
        steps : Generator[tuple[Maze, int, int], None, None]
            Generator from MazeGenerator.generate_animated().
        delay : float
            Seconds between frames.

        Returns
        -------
        Maze
            The completed maze.
        """
        maze = None
        rows = 0

        for maze, cx, cy in steps:
            if rows > 0:
                # Move cursor up to overwrite previous frame
                sys.stdout.write(f"\033[{rows}A")

            output = self._build_grid_string(maze, highlight=(cx, cy))
            rows = output.count("\n") + 1
            sys.stdout.write(output + "\n")
            sys.stdout.flush()
            time.sleep(delay)

        # Final clean render without highlight
        if maze is not None:
            sys.stdout.write(f"\033[{rows}A")
            output = self._build_grid_string(maze)
            sys.stdout.write(output + "\n")
            sys.stdout.flush()

        return maze

    def _build_grid_string(
        self,
        maze: Maze,
        show_path: bool = False,
        solution: list[Direction] | None = None,
        highlight: tuple[int, int] | None = None,
    ) -> str:
        """Build the maze grid as a string.

        Parameters
        ----------
        maze : Maze
            The maze to render.
        show_path : bool
            Whether to show the solution path.
        solution : list[Direction] | None
            The solution path directions.
        highlight : tuple[int, int] | None
            Cell to highlight (for animation).
        """
        path_cells = _compute_path_cells(maze, solution) if (
            show_path and solution
        ) else set()

        cs = self.color_scheme
        rows = 2 * maze.height + 1
        cols = 2 * maze.width + 1

        grid: list[list[str]] = [
            [" " for _ in range(cols)] for _ in range(rows)
        ]

        # Draw corners
        for gy in range(0, rows, 2):
            for gx in range(0, cols, 2):
                grid[gy][gx] = cs.wall + "+" + cs.reset

        # Draw horizontal walls (north/south)
        for y in range(maze.height):
            for x in range(maze.width):
                gx = 2 * x + 1
                if maze.has_wall(x, y, Direction.N):
                    gy_n = 2 * y
                    grid[gy_n][gx] = cs.wall + "-" + cs.reset
                if maze.has_wall(x, y, Direction.S):
                    gy_s = 2 * y + 2
                    grid[gy_s][gx] = cs.wall + "-" + cs.reset

        # Draw vertical walls (east/west)
        for y in range(maze.height):
            for x in range(maze.width):
                gy = 2 * y + 1
                if maze.has_wall(x, y, Direction.W):
                    gx_w = 2 * x
                    grid[gy][gx_w] = cs.wall + "|" + cs.reset
                if maze.has_wall(x, y, Direction.E):
                    gx_e = 2 * x + 2
                    grid[gy][gx_e] = cs.wall + "|" + cs.reset

        # Draw cell contents
        for y in range(maze.height):
            for x in range(maze.width):
                gx = 2 * x + 1
                gy = 2 * y + 1

                if highlight and (x, y) == highlight:
                    grid[gy][gx] = cs.path + "@" + cs.reset
                elif (x, y) == maze.entry:
                    grid[gy][gx] = cs.entry + "S" + cs.reset
                elif (x, y) == maze.exit_:
                    grid[gy][gx] = cs.exit_ + "E" + cs.reset
                elif (x, y) in maze.pattern_cells:
                    grid[gy][gx] = cs.pattern + "#" + cs.reset
                elif (x, y) in path_cells:
                    grid[gy][gx] = cs.path + "*" + cs.reset
                else:
                    grid[gy][gx] = " "

        return "\n".join("".join(row) for row in grid)


def _compute_path_cells(
    maze: Maze,
    solution: list[Direction] | None,
) -> set[tuple[int, int]]:
    """Convert a solution path into a set of (x, y) cell positions."""
    if not solution:
        return set()
    cells: set[tuple[int, int]] = set()
    x, y = maze.entry
    cells.add((x, y))
    for d in solution:
        dx, dy = DIRECTION_DELTA[d]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells
