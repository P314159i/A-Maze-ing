"""Main entry point for the A-Maze-ing project."""

import curses
import sys

from src.config_parser import ConfigError, ConfigParser, MazeConfig
from src.mazegen.maze_generator import Maze, MazeError
from src.mazegen.solver import SolverError
from src.output_writer import OutputError, OutputWriter
from src.visualizer import TerminalVisualizer


def get_config_filename() -> str:
    """Return the configuration filename from the command line.

    Returns:
        The configuration filename provided by the user.

    Raises:
        ConfigError: If exactly one configuration file is not provided.
    """
    if len(sys.argv) != 2:
        raise ConfigError(
            "Usage: python3 a_maze_ing.py <config_file.txt>"
        )

    return sys.argv[1]


def run() -> None:
    """Generate, solve, save, and display a maze."""
    config_filename: str = get_config_filename()
    config: MazeConfig = ConfigParser.parse(config_filename)

    maze = Maze(
        width=config.width,
        height=config.height,
        entry=config.entry_point,
        exitt=config.exit_point,
        perfect=config.perfect,
        myseed=config.seed,
    )

    maze.generate()
    solution: str = maze.solve()

    OutputWriter.write_output(
        config=config,
        maze=maze.get_grid(),
        solved_path=solution,
    )

    visualizer = TerminalVisualizer(maze, solution)
    visualizer.run()


def main() -> int:
    """Run the program and handle expected errors.

    Returns:
        Zero after successful execution, otherwise one.
    """
    try:
        run()
        return 0

    except (
        ConfigError,
        MazeError,
        SolverError,
        OutputError,
        ValueError,
        curses.error,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    except KeyboardInterrupt:
        print("\nProgram interrupted by user.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
