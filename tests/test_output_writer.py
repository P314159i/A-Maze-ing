from pathlib import Path

import pytest

from src.config_parser import MazeConfig
from src.output_writer import OutputError, OutputWriter


def _config(output_file: Path) -> MazeConfig:
    return MazeConfig(
        width=3,
        height=2,
        entry_point=(0, 0),
        exit_point=(2, 1),
        output_file=str(output_file),
        perfect=True,
        seed=42,
    )


def test_write_output_format(tmp_path: Path) -> None:
    """Write rows, blank line, coordinates, and solution in order."""
    output_file = tmp_path / "maze.txt"
    config = _config(output_file)
    maze = [
        [0x0, 0xA, 0xF],
        [0x1, 0x2, 0x3],
    ]

    OutputWriter.write_output(config, maze, "ES")

    assert output_file.read_text() == (
        "0af\n"
        "123\n"
        "\n"
        "0,0\n"
        "2,1\n"
        "ES\n"
    )


def test_write_output_overwrites_existing_file(tmp_path: Path) -> None:
    """Opening an existing output path replaces its old contents."""
    output_file = tmp_path / "maze.txt"
    output_file.write_text("old data")
    config = _config(output_file)

    OutputWriter.write_output(config, [[0xF]], "E")

    assert "old data" not in output_file.read_text()


def test_write_output_wraps_oserror(tmp_path: Path) -> None:
    """Convert file-system write failures into OutputError."""
    config = _config(tmp_path)

    with pytest.raises(OutputError, match="Could not write output file"):
        OutputWriter.write_output(config, [[0xF]], "E")
