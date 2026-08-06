"""Shortest-path solver for the A-Maze-ing project."""

from collections import deque
# import queue
from locale import currency
from os import path
from turtle import position, width
from typing import Deque, NoReturn


Coordinate = tuple[int, int]
NORTH: int = 1
EAST: int = 2
SOUTH: int = 4
WEST: int = 8


class SolverError(Exception):
    """Raises when the maze cannot be solved."""
    pass


class MazeSolver:
    """Finds the shortest path through a maze using BFS."""

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
        """Return shortest path as N, E, S, and W letters to show directions.

        Args:
            maze: Two-dimensional grid of wall bitmasks.
            entry: Starting coordinate.
            exit_position: Target coordinate.

        Returns:
            Shortest path encoded using N, E, S and W.

        Raises:
            SolverError: If the maze is invalid or no path exists.
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
    def _build_path(
        parent: dict[Coordinate, tuple[Coordinate, str]],
        entry_point: Coordinate,
        exit_point: Coordinate
    ) -> str:
        """Rebuilds the path from the BFS parent information."""
        directions: list[str] = []
        current: Coordinate = exit_point

        while current != entry_point:
            previous, direction = parent[current]
            directions.append(direction)
            current = previous

        directions.reverse()
        return "".join(directions)

    @classmethod
    def _find_reachable_neighbors(
        cls,
        maze: list[list[int]],
        position: Coordinate,
    ) -> list[tuple[Coordinate, str]]:
        """Return reachable neighbor cells."""
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
    def _validate_maze(maze: list[list[int]]) -> None:
        """validate the basic grid shape of maze and cell values."""
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
        """Validate a solver coordinate."""
        x, y = position
        if not (0 <= x < width and 0 <= y < height):
            raise SolverError(
                f"{name.capitalize()} position {position} "
                "is outside the maze"
            )
