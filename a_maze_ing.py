"""Main entry point for the A-Maze-ing project."""


import sys

from src.config_parser import ConfigError, MazeConfig, ConfigParser


def get_config_file_name() -> str:
    """Return the configuration filename from the command line."""
    if len(sys.argv) != 2:
        raise ConfigError("Usage: python3 a_maze_ing.py <config_file.txt>")
    return sys.argv[1]


def main() -> int:
    """Run the A-Maze-ing program."""

    try:
        filename: str = get_config_file_name()
        config: MazeConfig = ConfigParser.parse(filename)
        print(config)
        return 0
    except ConfigError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
