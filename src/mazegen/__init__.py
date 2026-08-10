from .maze_generator import Maze, MazeError

from .solver import MazeSolver, SolverError

# __all__ tells Python which names your module/package
# intentionally exposes as its public API,
# which also tells Flake8 to shut up
__all__ = ["Maze", "MazeError", "MazeSolver", "SolverError"]
