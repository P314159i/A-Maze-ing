"""Reusable maze generation package."""

from .maze_generator import Maze, MazeError
from .solver import MazeSolver, SolverError

# __all__ tells Python which names your module/package
# intentionally exposes as its public API.
__all__ = ["Maze", "MazeError", "MazeSolver", "SolverError"]
