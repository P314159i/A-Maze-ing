"""Tests for the maze configuration parser."""

from pathlib import Path

import pytest

from src.config_parser import ConfigError, ConfigParser, MazeConfig


def write_config(
    tmp_path: Path,
    content: str,
    filename: str = "config.txt",
) -> Path:
    """Create a temporary configuration file."""
    config_path: Path = tmp_path / filename
    config_path.write_text(content, encoding="utf-8")
    return config_path


def valid_config_text() -> str:
    """Return a complete valid configuration."""
    return (
        "WIDTH=20\n"
        "HEIGHT=18\n"
        "ENTRY=0,0\n"
        "EXIT=19,17\n"
        "OUTPUT_FILE=maze.txt\n"
        "PERFECT=False\n"
        "SEED=42\n"
    )


def test_parse_valid_config(tmp_path: Path) -> None:
    """A complete valid file should return MazeConfig."""
    config_path: Path = write_config(
        tmp_path,
        valid_config_text(),
    )

    config: MazeConfig = ConfigParser.parse(str(config_path))

    assert config.width == 20
    assert config.height == 18
    assert config.entry_point == (0, 0)
    assert config.exit_point == (19, 17)
    assert config.output_file == "maze.txt"
    assert config.perfect is False
    assert config.seed == 42


def test_parse_config_without_optional_seed(
    tmp_path: Path,
) -> None:
    """SEED may be omitted."""
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


def test_comments_and_blank_lines_are_ignored(
    tmp_path: Path,
) -> None:
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


def test_missing_file_raises_config_error(
    tmp_path: Path,
) -> None:
    """A missing file should become ConfigError."""
    missing_path: Path = tmp_path / "missing.txt"

    with pytest.raises(
        ConfigError,
        match="Could not read configuration file",
    ):
        ConfigParser.parse(str(missing_path))


def test_line_without_equals_sign_raises_error(
    tmp_path: Path,
) -> None:
    """Every setting must use KEY=VALUE syntax."""
    content: str = valid_config_text().replace(
        "WIDTH=20",
        "WIDTH 20",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="expected KEY=VALUE",
    ):
        ConfigParser.parse(str(config_path))


def test_empty_key_raises_error(tmp_path: Path) -> None:
    """A configuration key cannot be empty."""
    content: str = valid_config_text() + "=something\n"
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="key cannot be empty"):
        ConfigParser.parse(str(config_path))


def test_empty_value_raises_error(tmp_path: Path) -> None:
    """A configuration value cannot be empty."""
    content: str = valid_config_text().replace(
        "OUTPUT_FILE=maze.txt",
        "OUTPUT_FILE=",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="cannot be empty"):
        ConfigParser.parse(str(config_path))


def test_duplicate_key_raises_error(tmp_path: Path) -> None:
    """The same key must not be defined twice."""
    content: str = valid_config_text() + "WIDTH=30\n"
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="duplicate key 'WIDTH'"):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "missing_line, missing_key",
    [
        ("WIDTH=20\n", "WIDTH"),
        ("HEIGHT=18\n", "HEIGHT"),
        ("ENTRY=0,0\n", "ENTRY"),
        ("EXIT=19,17\n", "EXIT"),
        ("OUTPUT_FILE=maze.txt\n", "OUTPUT_FILE"),
        ("PERFECT=False\n", "PERFECT"),
    ],
)
def test_missing_required_key_raises_error(
    tmp_path: Path,
    missing_line: str,
    missing_key: str,
) -> None:
    """Every mandatory key must be provided."""
    content: str = valid_config_text().replace(
        missing_line,
        "",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match=missing_key):
        ConfigParser.parse(str(config_path))


def test_unknown_key_raises_error(tmp_path: Path) -> None:
    """Unsupported keys should be rejected."""
    content: str = valid_config_text() + "BANANA=42\n"
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="Unknown keys: BANANA",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "key, invalid_value",
    [
        ("WIDTH", "abc"),
        ("WIDTH", "20.5"),
        ("HEIGHT", "hello"),
        ("SEED", "four"),
    ],
)
def test_invalid_integer_raises_error(
    tmp_path: Path,
    key: str,
    invalid_value: str,
) -> None:
    """Integer fields must contain valid integer text."""
    content: str = valid_config_text()

    if key == "WIDTH":
        content = content.replace(
            "WIDTH=20",
            f"WIDTH={invalid_value}",
        )
    elif key == "HEIGHT":
        content = content.replace(
            "HEIGHT=18",
            f"HEIGHT={invalid_value}",
        )
    else:
        content = content.replace(
            "SEED=42",
            f"SEED={invalid_value}",
        )

    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match=f"'{key}' must be an integer",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "key, invalid_value",
    [
        ("WIDTH", "0"),
        ("WIDTH", "-1"),
        ("HEIGHT", "0"),
        ("HEIGHT", "-10"),
    ],
)
def test_dimensions_must_be_positive(
    tmp_path: Path,
    key: str,
    invalid_value: str,
) -> None:
    """Maze dimensions must be greater than zero."""
    content: str = valid_config_text()

    old_value: str = "20" if key == "WIDTH" else "18"
    content = content.replace(
        f"{key}={old_value}",
        f"{key}={invalid_value}",
    )

    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match=f"'{key}' must be greater than zero",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "coordinate",
    [
        "1",
        "1,2,3",
        "hello",
        "1;",
    ],
)
def test_coordinate_requires_x_y_format(
    tmp_path: Path,
    coordinate: str,
) -> None:
    """Coordinates must contain exactly two components."""
    content: str = valid_config_text().replace(
        "ENTRY=0,0",
        f"ENTRY={coordinate}",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="'ENTRY' must use the format x,y",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "coordinate",
    [
        ",1",
        "1,",
    ],
)
def test_coordinate_components_cannot_be_empty(
    tmp_path: Path,
    coordinate: str,
) -> None:
    """Both coordinate components must be present."""
    content: str = valid_config_text().replace(
        "ENTRY=0,0",
        f"ENTRY={coordinate}",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="must contain both x and y",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "coordinate",
    [
        "x,1",
        "1,y",
        "1.5,2",
    ],
)
def test_coordinate_components_must_be_integers(
    tmp_path: Path,
    coordinate: str,
) -> None:
    """Coordinate components must be integers."""
    content: str = valid_config_text().replace(
        "ENTRY=0,0",
        f"ENTRY={coordinate}",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="'ENTRY' must be an integer",
    ):
        ConfigParser.parse(str(config_path))


@pytest.mark.parametrize(
    "value",
    [
        "true",
        "false",
        "yes",
        "no",
        "1",
        "0",
    ],
)
def test_invalid_boolean_raises_error(
    tmp_path: Path,
    value: str,
) -> None:
    """PERFECT accepts only exact True or False."""
    content: str = valid_config_text().replace(
        "PERFECT=False",
        f"PERFECT={value}",
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
        "20,0",
        "0,18",
    ],
)
def test_entry_outside_maze_raises_error(
    tmp_path: Path,
    entry: str,
) -> None:
    """ENTRY must be inside the configured dimensions."""
    content: str = valid_config_text().replace(
        "ENTRY=0,0",
        f"ENTRY={entry}",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="ENTRY"):
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
    """EXIT must be inside the configured dimensions."""
    content: str = valid_config_text().replace(
        "EXIT=19,17",
        f"EXIT={exit_position}",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(ConfigError, match="EXIT"):
        ConfigParser.parse(str(config_path))


def test_entry_and_exit_must_be_different(
    tmp_path: Path,
) -> None:
    """ENTRY and EXIT cannot refer to the same cell."""
    content: str = valid_config_text().replace(
        "EXIT=19,17",
        "EXIT=0,0",
    )
    config_path: Path = write_config(tmp_path, content)

    with pytest.raises(
        ConfigError,
        match="ENTRY and EXIT must be different",
    ):
        ConfigParser.parse(str(config_path))
