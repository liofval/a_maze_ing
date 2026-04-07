"""A-Maze-ing: Maze generator with visual display.

Usage
-----
    python3 a_maze_ing.py config.txt
"""

from __future__ import annotations

import sys

from app.config import parse_config
from app.controller import MazeController
from app.display.terminal import TerminalDisplay
from app.formatter import write_maze_file
from mazegen.generator import MazeGenerator


def main() -> None:
    """Entry point for the A-Maze-ing program."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        sys.exit(1)

    try:
        config = parse_config(sys.argv[1])
    except (FileNotFoundError, ValueError) as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        generator = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit_=config.exit_,
            perfect=config.perfect,
            seed=config.seed,
            algorithm=config.algorithm,
        )
        maze = generator.generate()
        solution = generator.solve()
    except (ValueError, RuntimeError) as e:
        print(f"Generation error: {e}", file=sys.stderr)
        sys.exit(1)

    if solution is None:
        print("Error: No path found from entry to exit", file=sys.stderr)
        sys.exit(1)

    try:
        write_maze_file(maze, solution, config.output_file)
        print(f"Maze written to {config.output_file}")
    except OSError as e:
        print(f"Output error: {e}", file=sys.stderr)
        sys.exit(1)

    display = TerminalDisplay()
    controller = MazeController(generator, display)
    controller.run()


if __name__ == "__main__":
    main()
