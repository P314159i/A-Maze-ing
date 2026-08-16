"""
Reusable maze generation package.

Example:
    from mazegen import Maze

    maze = Maze(
        width=10,
        height=10,
        entry=(0, 0),
        exitt=(9, 9),
        perfect=True,
        myseed=42,
    )

    grid = maze.get_grid()
    solution = maze.solve()
"""

from .maze_generator import Maze, MazeError
from .solver import MazeSolver, SolverError

# __all__ tells Python which names your module/package
# intentionally exposes as its public API.
__all__ = ["Maze", "MazeError", "MazeSolver", "SolverError"]
