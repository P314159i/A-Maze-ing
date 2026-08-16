"""Tests for the maze configuration parser"""

import pytest

from pathlib import Path

from src.config_parser import ConfigParser, ConfigError, MazeConfig


def write_config(
        tmp_path: Path,
        content: str,
        filename: str = "config.txt",
) -> Path:
    """Create a temporary config file"""
    config_path: Path = tmp_path/filename
    config_path.write_text(content)
    return config_path


def test_parse_valid_config(tmp_path: Path) -> None:
    """Testing a complete valid file: should return MazeConfig."""
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "SEED=42\n"
    )
    config_path: Path = write_config(tmp_path, content)
    config: MazeConfig = ConfigParser.parse(str(config_path))

    assert config.width == 20
    assert config.height == 18
    assert config.entry_point == (0, 0)
    assert config.exit_point == (19, 17)
    assert config.output_file == "maze.txt"
    assert config.perfect is False
    assert config.seed == 42


def test_parse_config_without_seed(tmp_path: Path) -> None:
    """
    Testing without SEED: should return seed as None.
    and when perfect is True, should return perfect as True.
    """
    content: str = (
        "WIDTH=5\n"
        "HEIGHT=4\n"
        "ENTRY=0,0\n"
        "EXIT=4,3\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=True\n"
    )
    config_path: Path = write_config(tmp_path, content)
    config: MazeConfig = ConfigParser.parse(str(config_path))

    assert config.seed is None
    assert config.perfect is True


def test_comment_and_blank_lines_are_ignored(tmp_path: Path) -> None:
    """Comments and empty lines should not affect parsing."""
    content: str = (
        "# Maze configuration\n"
        "\n"
        "  WIDTH = 5  \n"
        "HEIGHT=4\n"
        "\n"
        "# Coordinates\n"
        "ENTRY = 0, 0\n"
        "EXIT = 4, 3\n"
        "OUTPUT_FILE = maze.txt\n"
        "PERFECT = False\n"
    )
    config_path: Path = write_config(tmp_path, content)
    config: MazeConfig = ConfigParser.parse(str(config_path))

    assert config.width == 5
    assert config.height == 4
    assert config.entry_point == (0, 0)
    assert config.exit_point == (4, 3)
    assert config.output_file == "maze.txt"
    assert config.perfect is False


def test_missing_file_raises_config_error(tmp_path: Path) -> None:
    """A missing file should raise the ConfigError"""
    missing_config_path: Path = tmp_path / "missing.txt"

    with pytest.raises(
        ConfigError,
        match="Could not read configuration file",
    ):
        ConfigParser.parse((str(missing_config_path)))


def test_line_without_equal_sign_raises_error(tmp_path: Path) -> None:
    """Every line must use KEY=VALUE setting."""
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT 19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "SEED=42\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="expected KEY=VALUE",
    ):
        ConfigParser.parse(str(config_path))


def test_empty_key_raises_error(tmp_path: Path) -> None:
    """Configuration key cannot be empty."""
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "SEED=42\n"
        "=emptykey"
    )
    config_path: Path = write_config(tmp_path, content)
    with pytest.raises(
        ConfigError,
        match="key cannot be empty"
    ):
        ConfigParser.parse(str(config_path))


def test_empty_value_raises_error(tmp_path: Path) -> None:
    """Configuration value cannot be empty."""
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "SEED=42\n"
    )
    config_path: Path = write_config(tmp_path, content)
    with pytest.raises(
        ConfigError,
        match="cannot be empty"
    ):
        ConfigParser.parse(str(config_path))


def test_duplicate_key_raises_error(tmp_path: Path) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "WIDTH=30\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="duplicate key 'WIDTH'"):
        ConfigParser.parse(str(config_path))


def test_missing_required_key_raises_error(tmp_path: Path) -> None:
    content: str = (
        "WIDTH=20\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="missing mandatory keys: HEIGHT"):
        ConfigParser.parse(str(config_path))


def test_unknown_key_raises_error(tmp_path: Path) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "UNKNOWN=value\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="Unknown keys: UNKNOWN"):
        ConfigParser.parse(str(config_path))


def test_invalid_integer_raises_error(tmp_path: Path) -> None:
    content: str = (
        "WIDTH=twenty\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="'WIDTH' must be an integer"):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    ("key", "invalid_value"),
    [
        ("WIDTH", "0"),
        ("WIDTH", "-1"),
        ("HEIGHT", "0"),
        ("HEIGHT", "-1"),
    ],
)
def test_dimensions_must_be_positive(
    tmp_path: Path,
    key: str,
    invalid_value: str,
) -> None:
    width: str = invalid_value if key == "WIDTH" else "20"
    height: str = invalid_value if key == "HEIGHT" else "18"
    content: str = (
        f"WIDTH={width}\n"
        f"HEIGHT={height}\n"
        "ENTRY=0,0\n"
        "EXIT=1,1\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match=rf"'{key}' must be greater than zero",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize("coordinate", ["0", "0,1,2"])
def test_coordinate_requires_x_y_format(
    tmp_path: Path,
    coordinate: str,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        f"ENTRY={coordinate}\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="must use the format x,y"):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize("coordinate", [",0", "0,"])
def test_coordinate_components_cannot_be_empty(
    tmp_path: Path,
    coordinate: str,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        f"ENTRY={coordinate}\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="must contain both x and y coordinates",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize("coordinate", ["x,0", "0,y"])
def test_coordinate_components_must_be_integers(
    tmp_path: Path,
    coordinate: str,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        f"ENTRY={coordinate}\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="'ENTRY' must be an integer"):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize("value", ["true", "FALSE", "yes", "1"])
def test_invalid_boolean_raises_error(
    tmp_path: Path,
    value: str,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        f"PERFECT={value}\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="'PERFECT' must be 'True' or 'False'",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "entry",
    [
        "-1,0",
        "0,-1",
        "20,17",
        "0,18",
    ],
)
def test_entry_outside_maze_raises_error(
    tmp_path: Path,
    entry: str,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        f"ENTRY={entry}\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="'ENTRY'.*outside"):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "exit_position",
    [
        "-1,0",
        "0,-1",
        "20,17",
        "19,18",
    ],
)
def test_exit_outside_maze_raises_error(
    tmp_path: Path,
    exit_position: str,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        f"EXIT={exit_position}\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="'EXIT'.*outside"):
        ConfigParser.parse(str(config_path))


def test_entry_and_exit_must_be_different(
    tmp_path: Path,
) -> None:
    content: str = (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=5,5\n"
        "EXIT=5,5\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="ENTRY and EXIT must be different",
    ):
        ConfigParser.parse(str(config_path))
