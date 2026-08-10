"""Shortest-path solver for the A-Maze-ing project."""

from collections import deque


Coordinate = tuple[int, int]
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8


class SolverError(Exception):
    """Raises when the maze cannot be solved."""
    pass


class MazeSolver:
    """Find the shortest path through a maze using BFS.

    The maze is represented as a two-dimensional list of integers.
    Each integer uses four bits to describe the closed walls of one
    cell:

    - Bit 0: North
    - Bit 1: East
    - Bit 2: South
    - Bit 3: West

    A bit value of 1 means that the wall is closed. A bit value of 0
    means that movement is allowed in that direction.
    """

    # Each direction contains:
    # (path_letter, x_change, y_change, wall_bit)
    DIRECTIONS: tuple[tuple[str, int, int, int], ...,] = (
        ("N", 0,  -1, NORTH),
        ("E", 1, 0, EAST),
        ("S", 0, 1, SOUTH),
        ("W", -1, 0, WEST),
    )

    @classmethod
    def find_shortest_path(
        cls,
        maze: list[list[int]],
        entry_point: Coordinate,
        exit_point: Coordinate,
    ) -> str:
        """
        Find the shortest path from the entry to the exit.

        This method uses the breadth-first search algorithm. BFS explores
        the maze level by level, which guarantees a shortest path when
        every movement has the same cost.

        Args:
            maze: Two-dimensional maze grid. Each cell contains an integer
                from 0 to 15 representing its closed walls.
            entry: Starting coordinate as an ``(x, y)`` tuple.
            exit_position: Destination coordinate as an ``(x, y)`` tuple.

        Returns:
            A string containing the shortest path using the letters
            ``N``, ``E``, ``S``, and ``W``. An empty string is returned
            when the entry and exit are the same position.

        Raises:
            SolverError: If the maze is invalid, a coordinate is outside
                the maze, or no path exists between entry and exit.
        """

        cls._validate_maze(maze)
        height: int = len(maze)
        width: int = len(maze[0])

        cls._validate_position(entry_point, width, height, "entry")
        cls._validate_position(exit_point, width, height, "exit")

        path_queue: deque[Coordinate] = deque([entry_point])
        visited: set[Coordinate] = {entry_point}
        parent: dict[Coordinate, tuple[Coordinate, str]] = {}

        while path_queue:
            current: Coordinate = path_queue.popleft()

            if current == exit_point:
                return cls._build_path(parent, entry_point, exit_point)

            for neighbor, direction in cls._find_reachable_neighbors(
                maze,
                current,
            ):
                if neighbor in visited:
                    continue
                visited.add(neighbor)
                parent[neighbor] = (current, direction)
                path_queue.append(neighbor)

        raise SolverError(
            f"No path found from {entry_point} to {exit_point}."
        )

    @staticmethod
    def _validate_maze(maze: list[list[int]]) -> None:
        """Validate the basic maze structure.

        The maze must contain at least one non-empty row. All rows must
        have the same width, and every cell must contain a valid wall
        value from 0 to 15.

        Args:
            maze: Two-dimensional maze grid to validate.

        Raises:
            SolverError: If the maze is empty, contains empty or uneven
                rows, or contains an invalid wall value.
        """
        if not maze:
            raise SolverError("Maze Cannot be Empty")

        width: int = len(maze[0])
        if width == 0:
            raise SolverError("Invalid maze: Maze has no rows.")

        for row_number, row in enumerate(maze):
            if len(row) != width:
                raise SolverError(f"Invalid row width for row {row_number}")

            for cell in row:
                if type(cell) is not int or not 0 <= cell <= 15:
                    raise SolverError(
                        f"Invalid wall value {cell}; "
                        "expected an integer from 0 to 15"
                    )

    @staticmethod
    def _validate_position(
        position: Coordinate,
        width: int,
        height: int,
        name: str,
    ) -> None:
        """Validate that a coordinate is inside the maze.

        Args:
            position: Coordinate to validate as an ``(x, y)`` tuple.
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            name: Human-readable coordinate name used in error messages,
                such as ``"entry"`` or ``"exit"``.

        Raises:
            SolverError: If the coordinate is outside the maze bounds.
        """
        x, y = position
        if not (0 <= x < width and 0 <= y < height):
            raise SolverError(
                f"{name.capitalize()} position {position} "
                "is outside the maze"
            )

    @classmethod
    def _find_reachable_neighbors(
        cls,
        maze: list[list[int]],
        position: Coordinate,
    ) -> list[tuple[Coordinate, str]]:
        """Return all reachable neighboring cells.

        The method checks the four cardinal directions. A neighboring
        cell is returned only when the corresponding wall is open and
        the neighboring coordinate remains inside the maze.

        Args:
            maze: Two-dimensional maze grid containing wall bitmasks.
            position: Current cell coordinate as an ``(x, y)`` tuple.

        Returns:
            A list of reachable neighbors. Each item contains the
            neighboring coordinate and the direction used to reach it,
            for example ``((2, 1), "E")``.
        """
        x, y = position
        height: int = len(maze)
        width: int = len(maze[0])
        walls: int = maze[y][x]
        neighbors: list[tuple[Coordinate, str]] = []

        for direction, dx, dy, wall_bit in cls.DIRECTIONS:
            if walls & wall_bit:
                continue

            neighbor_x: int = x + dx
            neighbor_y: int = y + dy

            if not (0 <= neighbor_x < width and 0 <= neighbor_y < height):
                continue

            neighbors.append(((neighbor_x, neighbor_y), direction))

        return neighbors

    @staticmethod
    def _build_path(
        parent: dict[Coordinate, tuple[Coordinate, str]],
        entry_point: Coordinate,
        exit_point: Coordinate
    ) -> str:
        """Reconstruct the path found by BFS
    
        BFS stores the previous cell and movement direction for every
        visited coordinate. This method starts at the exit, follows the
        stored parent information back to the entry, and reverses the
        collected directions.

        Args:
            parent: Mapping from a visited coordinate to a tuple containing
                its previous coordinate and the direction used to reach it.
            entry: Starting coordinate of the path.
            exit_position: Final coordinate of the path.

        Returns:
            The path from entry to exit as a string containing
            ``N``, ``E``, ``S``, and ``W``.
        """

        directions: list[str] = []
        current: Coordinate = exit_point

        while current != entry_point:
            previous, direction = parent[current]
            directions.append(direction)
            current = previous

        directions.reverse()
        return "".join(directions)
