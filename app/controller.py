"""Interactive controller for maze display.

Provides a menu-driven loop for regenerating the maze,
toggling the solution path, and changing wall colors.
"""

from __future__ import annotations

from mazegen.generator import MazeGenerator
from mazegen.maze import Direction
from app.display.terminal import TerminalDisplay


class MazeController:
    """Manages user interaction with the maze display.

    Parameters
    ----------
    generator : MazeGenerator
        The maze generator instance.
    display : TerminalDisplay
        The terminal display instance.
    """

    def __init__(
        self,
        generator: MazeGenerator,
        display: TerminalDisplay,
    ) -> None:
        self._generator = generator
        self._display = display
        self._show_path: bool = False
        self._solution: list[Direction] | None = None
        self._maze = generator.get_maze()
        self._solution = generator.solve()

    def run(self) -> None:
        """Run the interactive display loop."""
        self._render()

        while True:
            self._print_menu()
            try:
                choice = input("Choice? (1-4): ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if choice == "1":
                self._regenerate()
            elif choice == "2":
                self._toggle_path()
            elif choice == "3":
                self._change_colors()
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please enter 1-4.")

    def _render(self) -> None:
        """Render the current maze state."""
        self._display.render(
            self._maze,
            show_path=self._show_path,
            solution=self._solution,
        )

    def _regenerate(self) -> None:
        """Generate a new maze and display it."""
        self._maze = self._generator.generate()
        self._solution = self._generator.solve()
        self._show_path = False
        self._render()

    def _toggle_path(self) -> None:
        """Toggle the solution path display."""
        self._show_path = not self._show_path
        self._render()

    def _change_colors(self) -> None:
        """Cycle to the next color scheme and re-render."""
        self._display.cycle_colors()
        self._render()

    @staticmethod
    def _print_menu() -> None:
        """Print the interactive menu."""
        print("\n=== A-Maze-ing ===")
        print("1. Re-generate a new maze")
        print("2. Show/Hide path from entry to exit")
        print("3. Rotate maze colors")
        print("4. Quit")
