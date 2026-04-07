"""Tests for configuration file parser."""

import os
import tempfile

import pytest

from app.config import parse_config


def _write_config(content: str) -> str:
    """Write config content to a temp file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class TestParseConfig:
    """Tests for parse_config function."""

    def test_valid_config(self) -> None:
        path = _write_config(
            "WIDTH=20\nHEIGHT=15\nENTRY=0,0\n"
            "EXIT=19,14\nOUTPUT_FILE=out.txt\nPERFECT=True\n"
        )
        try:
            cfg = parse_config(path)
            assert cfg.width == 20
            assert cfg.height == 15
            assert cfg.entry == (0, 0)
            assert cfg.exit_ == (19, 14)
            assert cfg.perfect is True
        finally:
            os.unlink(path)

    def test_comments_ignored(self) -> None:
        path = _write_config(
            "# This is a comment\n"
            "WIDTH=10\nHEIGHT=10\nENTRY=0,0\n"
            "EXIT=9,9\nOUTPUT_FILE=out.txt\nPERFECT=False\n"
        )
        try:
            cfg = parse_config(path)
            assert cfg.width == 10
            assert cfg.perfect is False
        finally:
            os.unlink(path)

    def test_missing_key(self) -> None:
        path = _write_config("WIDTH=10\nHEIGHT=10\n")
        try:
            with pytest.raises(ValueError, match="Missing required"):
                parse_config(path)
        finally:
            os.unlink(path)

    def test_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            parse_config("/nonexistent/path.txt")

    def test_invalid_coords(self) -> None:
        path = _write_config(
            "WIDTH=10\nHEIGHT=10\nENTRY=abc\n"
            "EXIT=9,9\nOUTPUT_FILE=out.txt\nPERFECT=True\n"
        )
        try:
            with pytest.raises(ValueError):
                parse_config(path)
        finally:
            os.unlink(path)

    def test_out_of_bounds(self) -> None:
        path = _write_config(
            "WIDTH=10\nHEIGHT=10\nENTRY=0,0\n"
            "EXIT=20,20\nOUTPUT_FILE=out.txt\nPERFECT=True\n"
        )
        try:
            with pytest.raises(ValueError, match="out of bounds"):
                parse_config(path)
        finally:
            os.unlink(path)

    def test_optional_seed(self) -> None:
        path = _write_config(
            "WIDTH=10\nHEIGHT=10\nENTRY=0,0\n"
            "EXIT=9,9\nOUTPUT_FILE=out.txt\nPERFECT=True\nSEED=42\n"
        )
        try:
            cfg = parse_config(path)
            assert cfg.seed == 42
        finally:
            os.unlink(path)
