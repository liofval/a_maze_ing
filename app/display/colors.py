"""ANSI color management for terminal maze rendering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ColorScheme:
    """ANSI color codes for maze elements.

    Attributes
    ----------
    wall : str
        Color for maze walls.
    path : str
        Color for the solution path.
    entry : str
        Color for the entry marker.
    exit_ : str
        Color for the exit marker.
    pattern : str
        Color for the '42' pattern cells.
    reset : str
        ANSI reset code.
    """

    wall: str
    path: str
    entry: str
    exit_: str
    pattern: str
    reset: str = "\033[0m"


SCHEMES: list[ColorScheme] = [
    ColorScheme(
        wall="\033[37m",     # white
        path="\033[36m",     # cyan
        entry="\033[35m",    # magenta
        exit_="\033[31m",    # red
        pattern="\033[90m",  # dark gray
    ),
    ColorScheme(
        wall="\033[32m",     # green
        path="\033[36m",     # cyan
        entry="\033[35m",    # magenta
        exit_="\033[31m",    # red
        pattern="\033[34m",  # blue
    ),
    ColorScheme(
        wall="\033[33m",     # yellow
        path="\033[36m",     # cyan
        entry="\033[35m",    # magenta
        exit_="\033[31m",    # red
        pattern="\033[32m",  # green
    ),
    ColorScheme(
        wall="\033[34m",     # blue
        path="\033[33m",     # yellow
        entry="\033[32m",    # green
        exit_="\033[31m",    # red
        pattern="\033[35m",  # magenta
    ),
]
