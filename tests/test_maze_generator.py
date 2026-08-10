import pytest

from src.mazegen.maze_generator import Maze


def test_invalid_dimensions() -> None:
    """Check that zero or negative maze sizes are rejected."""

    with pytest.raises(ValueError):
        Maze(
            0,
            10,
            entry=(0, 0),
            exitt=(0, 1),
            perfect=True,
        )

    with pytest.raises(ValueError):
        Maze(
            10,
            0,
            entry=(0, 0),
            exitt=(1, 0),
            perfect=True,
        )

    with pytest.raises(ValueError):
        Maze(
            -5,
            10,
            entry=(0, 0),
            exitt=(0, 1),
            perfect=True,
        )


def test_invalid_entry_exit() -> None:
    """Check that entry and exit must be inside the maze."""

    with pytest.raises(ValueError):
        Maze(
            10,
            10,
            entry=(10, 0),
            exitt=(9, 9),
            perfect=True,
        )

    with pytest.raises(ValueError):
        Maze(
            10,
            10,
            entry=(-1, 0),
            exitt=(9, 9),
            perfect=True,
        )

    with pytest.raises(ValueError):
        Maze(
            10,
            10,
            entry=(0, 0),
            exitt=(0, 10),
            perfect=True,
        )

    with pytest.raises(ValueError):
        Maze(
            10,
            10,
            entry=(0, 0),
            exitt=(0, -1),
            perfect=True,
        )


def test_entry_equals_exit() -> None:
    """Check that entry and exit cannot be the same."""

    with pytest.raises(ValueError):
        Maze(
            10,
            10,
            entry=(2, 2),
            exitt=(2, 2),
            perfect=True,
        )


def test_same_seed_same_maze() -> None:
    """Check that the same seed produces the same maze."""

    maze1 = Maze(
        10,
        10,
        entry=(0, 0),
        exitt=(9, 9),
        perfect=True,
        myseed=42,
    )

    maze2 = Maze(
        10,
        10,
        entry=(0, 0),
        exitt=(9, 9),
        perfect=True,
        myseed=42,
    )

    maze1.generate()
    maze2.generate()

    assert maze1.get_grid() == maze2.get_grid()


def test_generate_grid_size() -> None:
    """Check that a 5x4 maze has 4 rows with 5 cells each."""

    maze = Maze(
        5,
        4,
        entry=(0, 0),
        exitt=(4, 3),
        perfect=True,
        myseed=42,
    )

    maze.generate()
    grid = maze.get_grid()

    assert len(grid) == 4
    assert all(len(row) == 5 for row in grid)


def test_wall_consistency() -> None:
    """Check that neighboring cells agree about shared walls."""

    maze = Maze(
        10,
        10,
        entry=(0, 0),
        exitt=(9, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()
    grid = maze.get_grid()

    for y in range(maze.height):
        for x in range(maze.width):
            if x + 1 < maze.width:
                assert bool(grid[y][x] & 0b0010) == bool(
                    grid[y][x + 1] & 0b1000
                )

            if y + 1 < maze.height:
                assert bool(grid[y][x] & 0b0100) == bool(
                    grid[y + 1][x] & 0b0001
                )


def test_solution_reaches_exit() -> None:
    """Check that the returned solution finishes at the exit."""

    maze = Maze(
        10,
        10,
        entry=(0, 0),
        exitt=(9, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()
    solution = maze.solve()

    x, y = maze.entry

    moves = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }

    for direction in solution:
        dx, dy = moves[direction]
        x += dx
        y += dy

    assert (x, y) == maze.exitt


def test_border_walls() -> None:
    """Check that all external maze borders stay closed."""

    maze = Maze(
        10,
        10,
        entry=(0, 0),
        exitt=(9, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()
    grid = maze.get_grid()

    for x in range(maze.width):
        assert grid[0][x] & 0b0001
        assert grid[maze.height - 1][x] & 0b0100

    for y in range(maze.height):
        assert grid[y][0] & 0b1000
        assert grid[y][maze.width - 1] & 0b0010


def test_42_pattern_cells_are_closed() -> None:
    """Check that every 42-pattern cell is fully closed."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()

    assert maze.pattern_cells

    for r, c in maze.pattern_cells:
        assert maze.grid[r][c].walls == 0b1111


def test_non_pattern_cells_are_connected() -> None:
    """Check that all non-42 cells remain connected."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()

    assert maze._all_corridors_connected()


def test_perfect_maze_has_no_loops() -> None:
    """Check that a perfect maze has no loops."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()

    assert maze._count_loops() == 0


def test_non_perfect_maze_has_at_least_two_loops() -> None:
    """Check that a non-perfect maze has at least two loops."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=False,
        myseed=42,
    )

    maze.generate()

    assert maze._count_loops() >= 2


def test_non_perfect_maze_has_multiple_entry_exit_routes() -> None:
    """Check that a non-perfect maze has more than one entry-exit route."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=False,
        myseed=42,
    )

    maze.generate()

    assert maze._has_two_entry_exit_routes()


def test_non_perfect_corners_and_center_are_open() -> None:
    """Check that corners and centre have at least two passages."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=False,
        myseed=42,
    )

    maze.generate()

    center_rows = {
        (maze.height - 1) // 2,
        maze.height // 2,
    }

    center_columns = {
        (maze.width - 1) // 2,
        maze.width // 2,
    }

    required_cells = {
        (0, 0),
        (0, maze.width - 1),
        (maze.height - 1, 0),
        (maze.height - 1, maze.width - 1),
    }

    for r in center_rows:
        for c in center_columns:
            required_cells.add((r, c))

    for r, c in required_cells:
        assert maze._open_degree(r, c) >= 2


def test_maze_has_no_open_3x3_area() -> None:
    """Check that the maze never contains a fully open 3x3 area."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=False,
        myseed=42,
    )

    maze.generate()

    assert not maze._has_3x3_open_area()


def test_same_seed_same_non_perfect_maze() -> None:
    """Check that the same seed reproduces a non-perfect maze."""

    maze1 = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=False,
        myseed=42,
    )

    maze2 = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=False,
        myseed=42,
    )

    maze1.generate()
    maze2.generate()

    assert maze1.get_grid() == maze2.get_grid()


def test_solution_uses_open_walls() -> None:
    """Check that every move in the solution goes through an open wall."""

    maze = Maze(
        20,
        10,
        entry=(0, 0),
        exitt=(19, 9),
        perfect=True,
        myseed=42,
    )

    maze.generate()
    solution = maze.solve()
    grid = maze.get_grid()

    x, y = maze.entry

    wall_bits = {
        "N": 0b0001,
        "E": 0b0010,
        "S": 0b0100,
        "W": 0b1000,
    }

    moves = {
        "N": (0, -1),
        "E": (1, 0),
        "S": (0, 1),
        "W": (-1, 0),
    }

    for direction in solution:
        assert not grid[y][x] & wall_bits[direction]

        dx, dy = moves[direction]
        x += dx
        y += dy

    assert (x, y) == maze.exitt


def test_multiple_sizes_and_seeds() -> None:
    """Check several maze sizes and seeds generate valid mazes."""

    sizes = [
        (5, 4),
        (10, 10),
        (20, 10),
        (10, 20),
    ]

    seeds = [0, 1, 42, 100]

    for width, height in sizes:
        for seed in seeds:
            maze = Maze(
                width,
                height,
                entry=(0, 0),
                exitt=(width - 1, height - 1),
                perfect=True,
                myseed=seed,
            )

            maze.generate()

            assert maze._all_corridors_connected()
            assert maze._walls_are_consistent()
            assert maze._borders_are_closed()
            assert not maze._has_3x3_open_area()
            assert maze._count_loops() == 0


def test_multiple_non_perfect_sizes_and_seeds() -> None:
    """Check several non-perfect mazes satisfy their rules."""

    sizes = [
        (10, 10),
        (20, 10),
        (10, 20),
    ]

    seeds = [0, 1, 42, 100]

    for width, height in sizes:
        for seed in seeds:
            maze = Maze(
                width,
                height,
                entry=(0, 0),
                exitt=(width - 1, height - 1),
                perfect=False,
                myseed=seed,
            )

            maze.generate()

            assert maze._all_corridors_connected()
            assert maze._walls_are_consistent()
            assert maze._borders_are_closed()
            assert not maze._has_3x3_open_area()
            assert maze._count_loops() >= 2
            assert maze._has_two_entry_exit_routes()
