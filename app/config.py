"""Configuration file parser for A-Maze-ing.

Reads KEY=VALUE pairs from a plain text file, validates
all required keys, and returns a frozen MazeConfig dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_KEYS = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}


@dataclass(frozen=True)
class MazeConfig:
    """Validated maze configuration.

    Attributes
    ----------
    width : int
        Maze width in cells.
    height : int
        Maze height in cells.
    entry : tuple[int, int]
        Entry coordinates (x, y).
    exit_ : tuple[int, int]
        Exit coordinates (x, y).
    output_file : str
        Path for the output maze file.
    perfect : bool
        Whether to generate a perfect maze.
    seed : int | None
        Random seed for reproducibility.
    algorithm : str
        Generation algorithm name.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "recursive_backtracker"


def parse_config(path: str) -> MazeConfig:
    """Parse a configuration file and return a validated MazeConfig.

    Parameters
    ----------
    path : str
        Path to the configuration file.

    Returns
    -------
    MazeConfig
        Parsed and validated configuration.

    Raises
    ------
    FileNotFoundError
        If the configuration file does not exist.
    ValueError
        If required keys are missing or values are invalid.
    """
    config_path = Path(path)
    if not config_path.is_file():
        raise FileNotFoundError(f"Config file not found: {path}")

    raw: dict[str, str] = {}
    with open(config_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                raise ValueError(
                    f"Line {line_num}: Invalid syntax (missing '='): {line}"
                )
            key, _, value = line.partition("=")
            raw[key.strip().upper()] = value.strip()

    missing = REQUIRED_KEYS - raw.keys()
    if missing:
        raise ValueError(f"Missing required keys: {', '.join(sorted(missing))}")

    width = _parse_positive_int(raw, "WIDTH")
    height = _parse_positive_int(raw, "HEIGHT")
    entry = _parse_coords(raw, "ENTRY")
    exit_ = _parse_coords(raw, "EXIT")
    output_file = raw["OUTPUT_FILE"]
    perfect = _parse_bool(raw, "PERFECT")
    seed = _parse_optional_int(raw, "SEED")
    algorithm = raw.get("ALGORITHM", "recursive_backtracker").lower()

    if not output_file:
        raise ValueError("OUTPUT_FILE must not be empty")

    _validate_bounds(width, height, entry, "ENTRY")
    _validate_bounds(width, height, exit_, "EXIT")

    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different")

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm,
    )


def _parse_positive_int(raw: dict[str, str], key: str) -> int:
    """Parse a positive integer value."""
    try:
        value = int(raw[key])
    except ValueError:
        raise ValueError(f"{key} must be an integer, got: {raw[key]}") from None
    if value <= 0:
        raise ValueError(f"{key} must be positive, got: {value}")
    return value


def _parse_coords(raw: dict[str, str], key: str) -> tuple[int, int]:
    """Parse 'x,y' coordinate string."""
    text = raw[key]
    parts = text.split(",")
    if len(parts) != 2:
        raise ValueError(f"{key} must be 'x,y', got: {text}")
    try:
        x, y = int(parts[0].strip()), int(parts[1].strip())
    except ValueError:
        raise ValueError(f"{key} coordinates must be integers: {text}") from None
    return (x, y)


def _parse_bool(raw: dict[str, str], key: str) -> bool:
    """Parse a boolean value (True/False, case-insensitive)."""
    text = raw[key].lower()
    if text in ("true", "1", "yes"):
        return True
    if text in ("false", "0", "no"):
        return False
    raise ValueError(f"{key} must be True or False, got: {raw[key]}")


def _parse_optional_int(
    raw: dict[str, str], key: str
) -> int | None:
    """Parse an optional integer value."""
    if key not in raw:
        return None
    try:
        return int(raw[key])
    except ValueError:
        raise ValueError(
            f"{key} must be an integer, got: {raw[key]}"
        ) from None


def _validate_bounds(
    width: int,
    height: int,
    coords: tuple[int, int],
    label: str,
) -> None:
    """Validate that coordinates are within maze bounds."""
    x, y = coords
    if not (0 <= x < width and 0 <= y < height):
        raise ValueError(
            f"{label} ({x},{y}) is out of bounds "
            f"for a {width}x{height} maze"
        )
