import dataclasses
from sys import exc_info
import pytest

from src.config_parser import ConfigError, MazeConfig, ConfigParser


def test_maze_config_stores_value() -> None:
    """Test that MazeConfig stores the supplied values correctly."""

    config = MazeConfig(
        width=20,
        height=18,
        entry=(0, 0),
        exit=(19, 17),
        output_file="maze.txt",
        perfect=False,
        seed=42,
    )

    assert config.width == 20
    assert config.height == 18
    assert config.entry == (0, 0)
    assert config.exit == (19, 17)
    assert config.output_file == "maze.txt"
    assert config.perfect is False
    assert config.seed == 42


def test_maze_config_is_frozen() -> None:
    """Test that MazeConfig is immutable (frozen)."""

    config = MazeConfig(
        width=20,
        height=18,
        entry=(0, 0),
        exit=(19, 17),
        output_file="maze.txt",
        perfect=True,
        seed=42,
    )

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.width = 25

    with pytest.raises(dataclasses.FrozenInstanceError):
        config.entry = (1, 1)


def test_maze_config_accepts_no_seed() -> None:
    """Test that MazeConfig accepts None for the seed value."""

    config = MazeConfig(
        width=20,
        height=18,
        entry=(0, 0),
        exit=(19, 17),
        output_file="maze.txt",
        perfect=True,
        seed=None,
    )

    assert config.seed is None


def test_config_error_message() -> None:
    """Test that ConfigError can be raised with a message."""

    # not good test
    with pytest.raises(ConfigError) as error_info:
        raise ConfigError("Invalid configuration")

    assert str(error_info.value) == "Invalid configuration"

    with pytest.raises(ConfigError, match="^Invalid WIDTH$"):
        raise ConfigError("Invalid WIDTH")


def test_clean_lines_trims_whitespace() -> None:
    lines: list[str] = [
        " WIDTH=20 \n",
        "\tHEIGHT=19\t\n",
        "\n",
        " \t\r ENTRY=1,0   \n",
        "# this is a comment.\n",
    ]

    result: list[str] = ConfigParser._strip_whitespace_and_comments(lines)
    assert result == [
        "WIDTH=20",
        "HEIGHT=19",
        "ENTRY=1,0",
    ]
