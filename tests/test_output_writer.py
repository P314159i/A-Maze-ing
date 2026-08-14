"""Tests for writing the generated maze output file."""

from pathlib import Path

import pytest

from src.config_parser import MazeConfig
from src.output_writer import OutputError, OutputWriter


def make_config(output_path: Path) -> MazeConfig:
    """Create a valid configuration for output-writer tests."""
    return MazeConfig(
        width=3,
        height=2,
        entry_point=(0, 0),
        exit_point=(2, 1),
        output_file=str(output_path),
        perfect=False,
        seed=42,
    )


def test_write_output_uses_required_file_format(
    tmp_path: Path,
) -> None:
    """Write hexadecimal rows, coordinates, and path exactly."""
    output_path: Path = tmp_path / "maze.txt"
    config: MazeConfig = make_config(output_path)
    maze: list[list[int]] = [
        [15, 10, 0],
        [1, 2, 3],
    ]

    OutputWriter.write_output(config, maze, "EES")

    assert output_path.read_text(encoding="utf-8") == (
        "fa0\n"
        "123\n"
        "\n"
        "0,0\n"
        "2,1\n"
        "EES\n"
    )


def test_write_output_overwrites_existing_file(
    tmp_path: Path,
) -> None:
    """Replace an existing output instead of appending to it."""
    output_path: Path = tmp_path / "maze.txt"
    output_path.write_text("old data", encoding="utf-8")
    config: MazeConfig = make_config(output_path)

    OutputWriter.write_output(config, [[15]], "")

    assert output_path.read_text(encoding="utf-8") == (
        "f\n\n0,0\n2,1\n\n"
    )


def test_write_output_wraps_operating_system_errors(
    tmp_path: Path,
) -> None:
    """Convert file-system failures into OutputError."""
    config: MazeConfig = make_config(tmp_path)

    with pytest.raises(
        OutputError,
        match="Could not write output file",
    ) as error_info:
        OutputWriter.write_output(config, [[15]], "")

    assert isinstance(error_info.value.__cause__, OSError)
