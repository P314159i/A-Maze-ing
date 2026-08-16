"""Tests for the breadth-first maze solver."""

from typing import cast

import pytest

from src.mazegen.solver import MazeSolver, SolverError


@pytest.mark.parametrize(
    "maze, entry, exit_point, expected_path",
    [
        ([[13, 7]], (0, 0), (1, 0), "E"),
        ([[13, 7]], (1, 0), (0, 0), "W"),
        ([[11], [14]], (0, 0), (0, 1), "S"),
        ([[11], [14]], (0, 1), (0, 0), "N"),
    ],
)
def test_find_shortest_path_in_each_direction(
    maze: list[list[int]],
    entry: tuple[int, int],
    exit_point: tuple[int, int],
    expected_path: str,
) -> None:
    """Return the correct path letter for every direction."""
    assert MazeSolver.find_shortest_path(
        maze,
        entry,
        exit_point,
    ) == expected_path


def test_entry_equal_to_exit_returns_empty_path() -> None:
    """No movement is needed when entry and exit are equal."""
    assert MazeSolver.find_shortest_path(
        [[15]],
        (0, 0),
        (0, 0),
    ) == ""


def test_breadth_first_search_returns_a_shortest_path() -> None:
    """Choose a two-step path in a fully connected 2x2 maze."""
    maze: list[list[int]] = [
        [9, 3],
        [12, 6],
    ]

    path: str = MazeSolver.find_shortest_path(
        maze,
        (0, 0),
        (1, 1),
    )

    assert path == "ES"
    assert len(path) == 2


def test_closed_cells_have_no_path() -> None:
    """Raise SolverError when no route reaches the exit."""
    with pytest.raises(SolverError, match="No path found"):
        MazeSolver.find_shortest_path(
            [[15, 15]],
            (0, 0),
            (1, 0),
        )


def test_empty_maze_is_rejected() -> None:
    """Reject a maze without rows."""
    with pytest.raises(SolverError, match="Maze Cannot be Empty"):
        MazeSolver.find_shortest_path([], (0, 0), (0, 0))


def test_maze_with_empty_row_is_rejected() -> None:
    """Reject a maze whose rows have no cells."""
    with pytest.raises(SolverError, match="Maze has no rows"):
        MazeSolver.find_shortest_path([[]], (0, 0), (0, 0))


def test_rows_must_have_equal_width() -> None:
    """Reject ragged maze grids."""
    with pytest.raises(SolverError, match="Invalid row width"):
        MazeSolver.find_shortest_path(
            [[15, 15], [15]],
            (0, 0),
            (1, 0),
        )


@pytest.mark.parametrize("invalid_cell", [-1, 16, True, 1.5, "1"])
def test_wall_values_must_be_integers_from_zero_to_fifteen(
    invalid_cell: object,
) -> None:
    """Reject values outside the four-bit wall representation."""
    maze: list[list[int]] = cast(
        list[list[int]],
        [[invalid_cell]],
    )

    with pytest.raises(SolverError, match="Invalid wall value"):
        MazeSolver.find_shortest_path(maze, (0, 0), (0, 0))


@pytest.mark.parametrize(
    "entry",
    [
        (-1, 0),
        (0, -1),
        (2, 0),
        (0, 1),
    ],
)
def test_entry_must_be_inside_maze(
    entry: tuple[int, int],
) -> None:
    """Reject entry coordinates outside the maze bounds."""
    with pytest.raises(SolverError, match="Entry position"):
        MazeSolver.find_shortest_path(
            [[13, 7]],
            entry,
            (1, 0),
        )


@pytest.mark.parametrize(
    "exit_point",
    [
        (-1, 0),
        (0, -1),
        (2, 0),
        (0, 1),
    ],
)
def test_exit_must_be_inside_maze(
    exit_point: tuple[int, int],
) -> None:
    """Reject exit coordinates outside the maze bounds."""
    with pytest.raises(SolverError, match="Exit position"):
        MazeSolver.find_shortest_path(
            [[13, 7]],
            (0, 0),
            exit_point,
        )
