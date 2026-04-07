"""Output file writer for A-Maze-ing.

Writes the maze to a file using hexadecimal wall encoding,
followed by entry/exit coordinates and the solution path.
"""

from __future__ import annotations

from mazegen.maze import Direction, Maze
from mazegen.solver import path_to_string


def write_maze_file(
    maze: Maze,
    solution: list[Direction],
    filepath: str,
) -> None:
    """Write the maze and solution to the output file.

    Format
    ------
    - One hex digit per cell, one row per line.
    - Empty line separator.
    - Entry coordinates (x,y).
    - Exit coordinates (x,y).
    - Solution path as N/E/S/W characters.

    Parameters
    ----------
    maze : Maze
        The generated maze.
    solution : list[Direction]
        The shortest path from entry to exit.
    filepath : str
        Output file path.
    """
    lines: list[str] = []

    for y in range(maze.height):
        row_hex = "".join(
            format(int(maze.get_cell(x, y).walls), "X")
            for x in range(maze.width)
        )
        lines.append(row_hex)

    lines.append("")

    ex, ey = maze.entry
    lines.append(f"{ex},{ey}")

    xx, xy = maze.exit_
    lines.append(f"{xx},{xy}")

    lines.append(path_to_string(solution))

    with open(filepath, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")
