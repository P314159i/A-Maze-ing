import pytest

from src.maze_generator import Maze


'''
This checks that class Maze correctly rejects 
  maze sizes that are 0 or negative
'''


def test_invalid_dimensions() -> None:
    with pytest.raises(ValueError):
        Maze(0, 10)

    with pytest.raises(ValueError):
        Maze(10, 0)

    with pytest.raises(ValueError):
        Maze(-5, 10)


'''
This checks that Maze class rejects entry or exit 
  coordinates outside the maze
'''


def test_invalid_entry_exit() -> None:
    with pytest.raises(ValueError):
        Maze(10, 10, entry=(10, 0))

    with pytest.raises(ValueError):
        Maze(10, 10, entry=(-1, 0))

    with pytest.raises(ValueError):
        Maze(10, 10, exit=(0, 10))

    with pytest.raises(ValueError):
        Maze(10, 10, exit=(0, -1))


'''
This checks if entry == exit : fail
'''


def test_entry_equals_exit() -> None:
    with pytest.raises(ValueError):
        Maze(10, 10, entry=(2, 2), exit=(2, 2))


'''
This checks that the same seed
  and same settings generate the same maze
'''


def test_same_seed_same_maze() -> None:
    maze1 = Maze(10, 10, myseed=42)
    maze2 = Maze(10, 10, myseed=42)

    maze1.generate()
    maze2.generate()

    assert maze1.get_grid() == maze2.get_grid()


'''
This checks that a 5 × 4 maze 
  produces 4 rows, each containing 5 wall values
  Just as a small non-square example 4&5, proves x&y are not swaped
  and maze is x&y in generated correct maze
'''


def test_generate_grid_size() -> None:
    maze = Maze(5, 4, myseed=42)

    maze.generate()
    grid = maze.get_grid()

    assert len(grid) == 4
    assert all(len(row) == 5 for row in grid)


'''
This checks that two neighbouring cells
  agree what is theird shared wall
     east ↔ west & south ↔ north
'''


def test_wall_consistency() -> None:
    maze = Maze(10, 10, myseed=42)
    maze.generate()
    grid = maze.get_grid()

    for y in range(maze.height):
        for x in range(maze.width):
            if x + 1 < maze.width:
                assert bool(grid[y][x] & 0b0010) == \
                    bool(grid[y][x + 1] & 0b1000)

            if y + 1 < maze.height:
                assert bool(grid[y][x] & 0b0100) == \
                    bool(grid[y + 1][x] & 0b0001)


'''
This checks that the path returned by BFS
  actually starts at entry and ends at exit
'''


def test_solution_reaches_exit() -> None:
    maze = Maze(
        10,
        10,
        myseed=42,
        entry=(0, 0),
        exit=(9, 9)
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

    assert (x, y) == maze.exit


'''
This verifies that the maze never opens a wall
  outside its external borders
'''


def test_border_walls() -> None:
    maze = Maze(10, 10, myseed=42)
    maze.generate()
    grid = maze.get_grid()

    for x in range(maze.width):
        assert grid[0][x] & 0b0001
        assert grid[maze.height - 1][x] & 0b0100

    for y in range(maze.height):
        assert grid[y][0] & 0b1000
        assert grid[y][maze.width - 1] & 0b0010
