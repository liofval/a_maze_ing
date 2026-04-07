"""Abstract base class for maze display implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from mazegen.maze import Direction, Maze


class MazeDisplay(ABC):
    """Interface for maze visualization backends.

    Implementations must render the maze grid including walls,
    entry/exit markers, and optionally the solution path.
    """

    @abstractmethod
    def render(
        self,
        maze: Maze,
        show_path: bool = False,
        solution: list[Direction] | None = None,
    ) -> None:
        """Render the maze to the display.

        Parameters
        ----------
        maze : Maze
            The maze to render.
        show_path : bool
            Whether to show the solution path.
        solution : list[Direction] | None
            The solution path (required if show_path is True).
        """
