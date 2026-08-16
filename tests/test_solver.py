import pytest

from src.mazegen.solver import MazeSolver, SolverError


def test_find_shortest_path() -> None:
    """Check that BFS returns the shortest route to the exit."""

    maze = [
        [0b1101, 0b1001, 0b1011],
        [0b1111, 0b1110, 0b1111],
    ]

    assert MazeSolver.find_shortest_path(maze, (0, 0), (2, 0)) == "EE"


def test_entry_equals_exit_returns_empty_path() -> None:
    """Check that no movement is needed when entry equals exit."""

    assert MazeSolver.find_shortest_path([[0b1111]], (0, 0), (0, 0)) == ""


def test_no_available_path_raises_solver_error() -> None:
    """Check that a fully blocked exit cannot be reached."""

    maze = [[0b1111, 0b1111]]

    with pytest.raises(SolverError, match="No path found"):
        MazeSolver.find_shortest_path(maze, (0, 0), (1, 0))


@pytest.mark.parametrize(
    "maze",
    [
        [],
        [[]],
        [[0b1111], [0b1111, 0b1111]],
    ],
)
def test_invalid_maze_structure_raises_solver_error(
    maze: list[list[int]],
) -> None:
    """Check that empty and uneven maze structures are rejected."""

    with pytest.raises(SolverError):
        MazeSolver.find_shortest_path(maze, (0, 0), (0, 0))


@pytest.mark.parametrize("wall_value", [-1, 16, True, 1.5, "1"])
def test_invalid_wall_values_raise_solver_error(wall_value: object) -> None:
    """Check that every cell uses an integer wall value from 0 to 15."""

    maze = [[wall_value]]

    with pytest.raises(SolverError, match="Invalid wall value"):
        MazeSolver.find_shortest_path(maze, (0, 0), (0, 0))  # type: ignore[arg-type]


@pytest.mark.parametrize("entry", [(-1, 0), (1, 0), (0, -1), (0, 1)])
def test_entry_outside_maze_raises_solver_error(
    entry: tuple[int, int],
) -> None:
    """Check that entry coordinates must be inside the maze."""

    with pytest.raises(SolverError, match="Entry position"):
        MazeSolver.find_shortest_path([[0b1111]], entry, (0, 0))


@pytest.mark.parametrize("exit_point", [(-1, 0), (1, 0), (0, -1), (0, 1)])
def test_exit_outside_maze_raises_solver_error(
    exit_point: tuple[int, int],
) -> None:
    """Check that exit coordinates must be inside the maze."""

    with pytest.raises(SolverError, match="Exit position"):
        MazeSolver.find_shortest_path([[0b1111]], (0, 0), exit_point)
