# """Main entry point for the A-Maze-ing project."""


# import sys

# from src.config_parser import ConfigError, MazeConfig, ConfigParser


# def get_config_file_name() -> str:
#     """Return the configuration filename from the command line."""
#     if len(sys.argv) != 2:
#         raise ConfigError("Usage: python3 a_maze_ing.py <config_file.txt>")
#     return sys.argv[1]


# def main() -> int:
#     """Run the A-Maze-ing program."""

#     try:
#         filename: str = get_config_file_name()
#         config: MazeConfig = ConfigParser.parse(filename)
#         print(config)
#         return 0
#     except ConfigError as error:
#         print(f"Configuration error: {error}", file=sys.stderr)
#         return 1


# if __name__ == "__main__":
#     sys.exit(main())


"""Temporary main program for testing the parser, solver, and writer."""

import sys

from src.config_parser import ConfigError, ConfigParser, MazeConfig
from src.output_writer import OutputError, OutputWriter
from src.solver import MazeSolver, SolverError


def get_config_filename() -> str:
    """Return the configuration filename from the command line.

    Returns:
        The configuration filename supplied by the user.

    Raises:
        ConfigError: If exactly one filename is not provided.
    """
    if len(sys.argv) != 2:
        raise ConfigError(
            "Usage: python3 a_maze_ing.py <config_file>"
        )

    return sys.argv[1]


def create_test_maze(config: MazeConfig) -> list[list[int]]:
    """Create a temporary hardcoded maze for testing.

    The temporary maze is three cells wide and three cells high.
    Its shortest path from ``(0, 0)`` to ``(2, 2)`` is ``EESS``.

    Args:
        config: Validated maze configuration.

    Returns:
        A hardcoded three-by-three maze.

    Raises:
        ConfigError: If the configuration does not match the test maze.
    """
    if config.width != 10 or config.height != 10:
        raise ConfigError(
            "Temporary test maze requires WIDTH=3 and HEIGHT=3"
        )


    maze: list[list[int]] = [
        [13, 5, 3, 9, 5, 5, 3, 9, 5, 3],
        [9, 3, 12, 6, 13, 3, 12, 6, 11, 10],
        [10, 12, 5, 3, 9, 2, 9, 5, 2, 10],
        [10, 13, 5, 4, 6, 14, 12, 3, 12, 6],
        [10, 9, 5, 5, 5, 1, 3, 10, 13, 3],
        [8, 6, 9, 3, 9, 6, 14, 10, 9, 2],
        [12, 5, 6, 10, 12, 5, 3, 12, 6, 10],
        [9, 7, 9, 6, 13, 3, 12, 5, 5, 6],
        [10, 9, 6, 9, 5, 4, 5, 5, 3, 11],
        [12, 4, 5, 6, 13, 5, 5, 5, 4, 6],
    ]

    return maze


def run() -> None:
    """Parse, solve, and write the temporary test maze."""
    config_filename: str = get_config_filename()

    config: MazeConfig = ConfigParser.parse(
        config_filename
    )

    maze: list[list[int]] = create_test_maze(config)

    path: str = MazeSolver.find_shortest_path(
        maze,
        config.entry,
        config.exit,
    )

    OutputWriter.write_output(
        config,
        maze,
        path,
    )

    print(
        f"Maze successfully written to "
        f"'{config.output_file}'"
    )
    print(f"Shortest path: {path}")


def main() -> int:
    """Run the program and handle expected errors.

    Returns:
        Zero when the program succeeds, or one when an error occurs.
    """
    try:
        run()
        return 0

    except (
        ConfigError,
        SolverError,
        OutputError,
    ) as error:
        print(
            f"Error: {error}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
