import random

from .solver import MazeSolver


Coordinate = tuple[int, int]
Edge = tuple[Coordinate, Coordinate]


PATTERN_42: tuple[str, ...] = (
    "1010111",
    "1010001",
    "1110111",
    "0010100",
    "0010111",
)


class MazeError(RuntimeError):
    """Raised when a maze cannot satisfy generation requirements."""


class Maze:
    class Cell:
        """Store one cell of the maze."""

        def __init__(
                self,
                r: int,
                c: int,
                walls: int = 0b1111,
                visited: bool = False
                ) -> None:
            """Initialize a maze cell."""
            self.r = r
            self.c = c
            self.walls = walls
            self.visited = visited

    def __init__(
            self,
            width: int,
            height: int,
            entry: tuple[int, int],
            exitt: tuple[int, int],
            perfect: bool,
            myseed: int | None = None,
            ) -> None:
        """Initialize the maze."""

        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be positive")

        if not perfect and (width - 1) * (height - 1) < 2:
            raise ValueError(
                "Non-perfect maze is too small for two independent loops"
            )

        self.width = width
        self.height = height
        self.myseed = myseed
        self.rndm = random.Random(myseed)
        self.entry = entry
        self.perfect = perfect
        self.exitt = exitt

        # stores the row, column positions used by the 42
        self.pattern_cells: set[tuple[int, int]] = set()

        if not (
            0 <= self.entry[0] < width
            and 0 <= self.entry[1] < height
        ):
            raise ValueError("Entry is outside the maze")

        if not (
            0 <= self.exitt[0] < width
            and 0 <= self.exitt[1] < height
        ):
            raise ValueError("Exit is outside the maze")

        if self.entry == self.exitt:
            raise ValueError("Entry and exit must be different")

        # grid[row][column]
        self.grid: list[list["Maze.Cell"]] = [
            [self.Cell(r, c) for c in range(width)]
            for r in range(height)
        ]

    def reset(self) -> None:
        """Reset all cells before generating a new maze."""
        self.pattern_cells.clear()

        for row in self.grid:
            for cell in row:
                cell.walls = 0b1111
                cell.visited = False

    def generate(self) -> None:
        """Generate the maze."""
        self.reset()
        self.rndm.seed(self.myseed)

        # place 42 before DFS so DFS knows not to enter those cells
        self._place_42_pattern()

        # entry is (x, y), so column = x and row = y
        start_c, start_r = self.entry

        self.grid[start_r][start_c].visited = True

        stack: list["Maze.Cell"] = [
            self.grid[start_r][start_c]
        ]

        directions = [
            (-1, 0),  # north
            (1, 0),   # south
            (0, -1),  # west
            (0, 1),   # east
        ]

        while stack:
            current = stack[-1]
            neighbors: list["Maze.Cell"] = []

            for d_r, d_c in directions:
                n_r = current.r + d_r
                n_c = current.c + d_c

                if (
                    0 <= n_r < self.height
                    and 0 <= n_c < self.width
                    and (n_r, n_c) not in self.pattern_cells
                    and not self.grid[n_r][n_c].visited
                ):
                    neighbors.append(
                        self.grid[n_r][n_c]
                    )

            if neighbors:
                next_cell = self.rndm.choice(neighbors)

                # *DFS*
                # Walls are stored as 4 bit binary.
                # Bit 0 = north
                # Bit 1 = east
                # Bit 2 = south
                # Bit 3 = west

                # Binary Mask =
                # north: 0b1110
                # east:  0b1101
                # south: 0b1011
                # west:  0b0111

                if next_cell.r > current.r:  # south
                    current.walls &= 0b1011
                    next_cell.walls &= 0b1110

                elif next_cell.r < current.r:  # north
                    current.walls &= 0b1110
                    next_cell.walls &= 0b1011

                elif next_cell.c > current.c:  # east
                    current.walls &= 0b1101
                    next_cell.walls &= 0b0111

                elif next_cell.c < current.c:  # west
                    current.walls &= 0b0111
                    next_cell.walls &= 0b1101

                next_cell.visited = True
                stack.append(next_cell)

            else:
                stack.pop()

        if not self.perfect:
            self.make_non_perfect()

        self._validate_generated_maze()

    def make_non_perfect(self) -> None:
        """Add the extra passages required by a non-perfect maze."""

        self._open_required_corridors()
        self._ensure_two_independent_loops()
        self._ensure_two_entry_exit_routes()

        dead_ends: list[tuple[int, int]] = []

        for r in range(self.height):
            for c in range(self.width):

                # never modify a 42 cell
                if (r, c) in self.pattern_cells:
                    continue

                cell = self.grid[r][c]

                if cell.walls.bit_count() == 3:
                    dead_ends.append((r, c))

        self.rndm.shuffle(dead_ends)

        while dead_ends:
            changed = False

            for r, c in dead_ends:
                if self._open_degree(r, c) != 1:
                    continue

                cell = self.grid[r][c]
                possible_walls: list[tuple[int, int]] = []

                # north
                if (
                    r > 0
                    and (r - 1, c) not in self.pattern_cells
                    and cell.walls & 0b0001
                ):
                    possible_walls.append((r - 1, c))

                # east
                if (
                    c < self.width - 1
                    and (r, c + 1) not in self.pattern_cells
                    and cell.walls & 0b0010
                ):
                    possible_walls.append((r, c + 1))

                # south
                if (
                    r < self.height - 1
                    and (r + 1, c) not in self.pattern_cells
                    and cell.walls & 0b0100
                ):
                    possible_walls.append((r + 1, c))

                # west
                if (
                    c > 0
                    and (r, c - 1) not in self.pattern_cells
                    and cell.walls & 0b1000
                ):
                    possible_walls.append((r, c - 1))

                self.rndm.shuffle(possible_walls)

                for n_r, n_c in possible_walls:
                    if self._try_open_wall(r, c, n_r, n_c):
                        changed = True
                        break

            if not changed:
                break

            dead_ends = self._dead_end_cells()

    def _open_wall(
            self,
            r: int,
            c: int,
            n_r: int,
            n_c: int,
            ) -> None:
        '''
        Open the wall between two neighboring cells
        '''

        if n_c > c:  # east
            self.grid[r][c].walls &= 0b1101
            self.grid[n_r][n_c].walls &= 0b0111

        elif n_c < c:  # west
            self.grid[r][c].walls &= 0b0111
            self.grid[n_r][n_c].walls &= 0b1101

        elif n_r > r:  # south
            self.grid[r][c].walls &= 0b1011
            self.grid[n_r][n_c].walls &= 0b1110

        elif n_r < r:  # north
            self.grid[r][c].walls &= 0b1110
            self.grid[n_r][n_c].walls &= 0b1011

    def _close_wall(
            self,
            r: int,
            c: int,
            n_r: int,
            n_c: int,
            ) -> None:
        """Close the wall between two neighboring cells."""

        if n_c > c:  # east
            self.grid[r][c].walls |= 0b0010
            self.grid[n_r][n_c].walls |= 0b1000

        elif n_c < c:  # west
            self.grid[r][c].walls |= 0b1000
            self.grid[n_r][n_c].walls |= 0b0010

        elif n_r > r:  # south
            self.grid[r][c].walls |= 0b0100
            self.grid[n_r][n_c].walls |= 0b0001

        elif n_r < r:  # north
            self.grid[r][c].walls |= 0b0001
            self.grid[n_r][n_c].walls |= 0b0100

    def _try_open_wall(
            self,
            r: int,
            c: int,
            n_r: int,
            n_c: int,
            ) -> bool:
        """Try opening a wall without creating a 3x3 open area."""

        if (
            (r, c) in self.pattern_cells
            or (n_r, n_c) in self.pattern_cells
        ):
            return False

        if not self._wall_is_closed(r, c, n_r, n_c):
            return False

        self._open_wall(r, c, n_r, n_c)

        if self._has_3x3_open_area():
            self._close_wall(r, c, n_r, n_c)
            return False

        return True

    def _wall_is_closed(
            self,
            r: int,
            c: int,
            n_r: int,
            n_c: int,
            ) -> bool:
        """Return whether the wall between two cells is closed."""

        if n_c > c:
            return bool(self.grid[r][c].walls & 0b0010)

        if n_c < c:
            return bool(self.grid[r][c].walls & 0b1000)

        if n_r > r:
            return bool(self.grid[r][c].walls & 0b0100)

        return bool(self.grid[r][c].walls & 0b0001)

    def _open_degree(self, r: int, c: int) -> int:
        """Count how many passages leave one cell."""
        degree = 0
        cell = self.grid[r][c]

        directions = (
            (-1, 0, 0b0001),
            (0, 1, 0b0010),
            (1, 0, 0b0100),
            (0, -1, 0b1000),
        )

        for d_r, d_c, wall_bit in directions:
            n_r = r + d_r
            n_c = c + d_c

            if not (
                0 <= n_r < self.height
                and 0 <= n_c < self.width
            ):
                continue

            if (n_r, n_c) in self.pattern_cells:
                continue

            if not cell.walls & wall_bit:
                degree += 1

        return degree

    def _closed_neighbors(
            self,
            r: int,
            c: int,
            ) -> list[tuple[int, int]]:
        """Return neighbors separated from a cell by a closed wall."""

        neighbors: list[tuple[int, int]] = []
        cell = self.grid[r][c]

        directions = (
            (-1, 0, 0b0001),
            (0, 1, 0b0010),
            (1, 0, 0b0100),
            (0, -1, 0b1000),
        )

        for d_r, d_c, wall_bit in directions:
            n_r = r + d_r
            n_c = c + d_c

            if not (
                0 <= n_r < self.height
                and 0 <= n_c < self.width
            ):
                continue

            if (n_r, n_c) in self.pattern_cells:
                continue

            if cell.walls & wall_bit:
                neighbors.append((n_r, n_c))

        return neighbors

    def _candidate_closed_walls(
            self,
            ) -> list[tuple[int, int, int, int]]:
        """Return internal closed walls that may be opened."""

        possible_walls: list[tuple[int, int, int, int]] = []

        for r in range(self.height):
            for c in range(self.width):

                if (r, c) in self.pattern_cells:
                    continue

                if (
                    c + 1 < self.width
                    and (r, c + 1) not in self.pattern_cells
                    and self.grid[r][c].walls & 0b0010
                ):
                    possible_walls.append(
                        (r, c, r, c + 1)
                    )

                if (
                    r + 1 < self.height
                    and (r + 1, c) not in self.pattern_cells
                    and self.grid[r][c].walls & 0b0100
                ):
                    possible_walls.append(
                        (r, c, r + 1, c)
                    )

        return possible_walls

    def _center_cells(self) -> set[tuple[int, int]]:
        """Return the central cell or cells of the maze."""
        center_rows = {
            (self.height - 1) // 2,
            self.height // 2,
        }

        center_columns = {
            (self.width - 1) // 2,
            self.width // 2,
        }

        return {
            (r, c)
            for r in center_rows
            for c in center_columns
        }

    def _required_non_perfect_cells(
            self,
            ) -> set[tuple[int, int]]:
        """Return corners and centre cells that must be corridors."""

        required = {
            (0, 0),
            (0, self.width - 1),
            (self.height - 1, 0),
            (self.height - 1, self.width - 1),
        }

        required.update(self._center_cells())

        return required

    def _open_required_corridors(self) -> None:
        """Keep the four corners and centre as open corridors."""
        required = self._required_non_perfect_cells()

        for r, c in required:
            while self._open_degree(r, c) < 2:
                possible_walls = self._closed_neighbors(r, c)
                self.rndm.shuffle(possible_walls)

                opened = False

                for n_r, n_c in possible_walls:
                    if self._try_open_wall(r, c, n_r, n_c):
                        opened = True
                        break

                if not opened:
                    raise MazeError(
                        "Could not keep corners and centre "
                        "as open corridors"
                    )

    def _ensure_two_independent_loops(self) -> None:
        """Ensure that a non-perfect maze contains at least two loops."""
        possible_walls = self._candidate_closed_walls()
        self.rndm.shuffle(possible_walls)

        for r, c, n_r, n_c in possible_walls:
            if self._count_loops() >= 2:
                return

            self._try_open_wall(r, c, n_r, n_c)

        if self._count_loops() < 2:
            raise MazeError(
                "Could not create two independent loops"
            )

    def _count_loops(self) -> int:
        """Return the number of independent cycles in the maze."""
        cells = (
            self.width * self.height
            - len(self.pattern_cells)
        )

        passages = 0

        for r in range(self.height):
            for c in range(self.width):

                if (r, c) in self.pattern_cells:
                    continue

                if (
                    c + 1 < self.width
                    and (r, c + 1) not in self.pattern_cells
                    and not self.grid[r][c].walls & 0b0010
                ):
                    passages += 1

                if (
                    r + 1 < self.height
                    and (r + 1, c) not in self.pattern_cells
                    and not self.grid[r][c].walls & 0b0100
                ):
                    passages += 1

        return passages - cells + 1

    def _passage_neighbors(
            self,
            r: int,
            c: int,
            blocked_edge: Edge | None = None,
            ) -> list[Coordinate]:
        """Return cells reachable through open passages."""

        neighbors: list[Coordinate] = []
        cell = self.grid[r][c]
        current = (r, c)

        directions = (
            (-1, 0, 0b0001),
            (0, 1, 0b0010),
            (1, 0, 0b0100),
            (0, -1, 0b1000),
        )

        for d_r, d_c, wall_bit in directions:
            n_r = r + d_r
            n_c = c + d_c
            neighbor = (n_r, n_c)

            if not (
                0 <= n_r < self.height
                and 0 <= n_c < self.width
            ):
                continue

            if neighbor in self.pattern_cells:
                continue

            if cell.walls & wall_bit:
                continue

            if blocked_edge is not None:
                first, second = blocked_edge

                if (
                    (current == first and neighbor == second)
                    or
                    (current == second and neighbor == first)
                ):
                    continue

            neighbors.append(neighbor)

        return neighbors

    def _find_entry_exit_path(self) -> list[Edge] | None:
        """Find one existing path between entry and exit."""

        start_c, start_r = self.entry
        exit_c, exit_r = self.exitt

        start = (start_r, start_c)
        destination = (exit_r, exit_c)

        stack: list[Coordinate] = [start]
        visited: set[Coordinate] = {start}
        parent: dict[Coordinate, Coordinate] = {}

        while stack:
            current = stack.pop()

            if current == destination:
                path: list[Coordinate] = [destination]

                while path[-1] != start:
                    path.append(parent[path[-1]])

                path.reverse()

                return [
                    (path[index], path[index + 1])
                    for index in range(len(path) - 1)
                ]

            for neighbor in self._passage_neighbors(
                current[0],
                current[1],
            ):
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                parent[neighbor] = current
                stack.append(neighbor)

        return None

    def _path_exists(
            self,
            blocked_edge: Edge | None = None,
            ) -> bool:
        """Check whether entry can reach exit."""

        start_c, start_r = self.entry
        exit_c, exit_r = self.exitt

        start = (start_r, start_c)
        destination = (exit_r, exit_c)

        stack: list[Coordinate] = [start]
        visited: set[Coordinate] = {start}

        while stack:
            current = stack.pop()

            if current == destination:
                return True

            for neighbor in self._passage_neighbors(
                current[0],
                current[1],
                blocked_edge,
            ):
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                stack.append(neighbor)

        return False

    def _has_two_entry_exit_routes(self) -> bool:
        """Check that entry and exit have more than one route."""

        first_path = self._find_entry_exit_path()

        if first_path is None:
            return False

        for edge in first_path:
            if self._path_exists(blocked_edge=edge):
                return True

        return False

    def _ensure_two_entry_exit_routes(self) -> None:
        """Create another entry-to-exit route if necessary."""

        if self._has_two_entry_exit_routes():
            return

        possible_walls = self._candidate_closed_walls()
        self.rndm.shuffle(possible_walls)

        for r, c, n_r, n_c in possible_walls:
            self._try_open_wall(r, c, n_r, n_c)

            if self._has_two_entry_exit_routes():
                return

        raise MazeError(
            "Could not create two different entry-to-exit routes"
        )

    def _dead_end_cells(self) -> list[tuple[int, int]]:
        """Return all non-pattern dead-end cells."""
        return [
            (r, c)
            for r in range(self.height)
            for c in range(self.width)
            if (
                (r, c) not in self.pattern_cells
                and self._open_degree(r, c) == 1
            )
        ]

    def _has_3x3_open_area(self) -> bool:
        """Check whether the maze contains a fully open 3x3 area."""

        if self.width < 3 or self.height < 3:
            return False

        for top in range(self.height - 2):
            for left in range(self.width - 2):

                is_open = True

                for r in range(top, top + 3):
                    for c in range(left, left + 2):

                        if self.grid[r][c].walls & 0b0010:
                            is_open = False
                            break

                    if not is_open:
                        break

                if not is_open:
                    continue

                for r in range(top, top + 2):
                    for c in range(left, left + 3):

                        if self.grid[r][c].walls & 0b0100:
                            is_open = False
                            break

                    if not is_open:
                        break

                if is_open:
                    return True

        return False

    def _place_42_pattern(self) -> None:
        """Place the closed-cell 42 pattern inside the maze."""

        pattern_height = len(PATTERN_42)
        pattern_width = len(PATTERN_42[0])

        # leave one corridor around the pattern
        if (
            self.height < pattern_height + 2
            or self.width < pattern_width + 2
        ):
            print("Error: maze is too small for the 42 pattern")
            return

        entry_c, entry_r = self.entry
        exit_c, exit_r = self.exitt

        protected: set[tuple[int, int]] = {
            (entry_r, entry_c),
            (exit_r, exit_c),
        }

        # PERFECT=False requires the centre to stay open
        if not self.perfect:
            protected.update(self._center_cells())

        for top in range(
            1,
            self.height - pattern_height,
        ):
            for left in range(
                1,
                self.width - pattern_width,
            ):

                pattern_cells: set[tuple[int, int]] = set()

                for pattern_r, line in enumerate(PATTERN_42):
                    for pattern_c, value in enumerate(line):

                        if value == "1":
                            pattern_cells.add(
                                (
                                    top + pattern_r,
                                    left + pattern_c,
                                )
                            )

                if pattern_cells & protected:
                    continue

                if not self.perfect:
                    if not self._required_cells_have_room(
                        pattern_cells
                    ):
                        continue

                if not self._pattern_keeps_maze_connected(
                    pattern_cells
                ):
                    continue

                self.pattern_cells = pattern_cells

                for r, c in self.pattern_cells:
                    self.grid[r][c].walls = 0b1111

                return

        print("Error: no safe place for the 42 pattern")

    def _required_cells_have_room(
            self,
            pattern_cells: set[tuple[int, int]],
            ) -> bool:
        """Check that required corridor cells still have two neighbors."""

        required = self._required_non_perfect_cells()

        directions = (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        )

        for r, c in required:

            if (r, c) in pattern_cells:
                return False

            available_neighbors = 0

            for d_r, d_c in directions:
                n_r = r + d_r
                n_c = c + d_c

                if (
                    0 <= n_r < self.height
                    and 0 <= n_c < self.width
                    and (n_r, n_c) not in pattern_cells
                ):
                    available_neighbors += 1

            if available_neighbors < 2:
                return False

        return True

    def _pattern_keeps_maze_connected(
            self,
            pattern_cells: set[tuple[int, int]],
            ) -> bool:
        """Check connectivity if the 42 cells are removed."""

        start_c, start_r = self.entry
        start = (start_r, start_c)

        if start in pattern_cells:
            return False

        visited: set[Coordinate] = {start}
        stack: list[Coordinate] = [start]

        directions = (
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
        )

        while stack:
            r, c = stack.pop()

            for d_r, d_c in directions:
                n_r = r + d_r
                n_c = c + d_c

                if not (
                    0 <= n_r < self.height
                    and 0 <= n_c < self.width
                ):
                    continue

                if (n_r, n_c) in pattern_cells:
                    continue

                if (n_r, n_c) in visited:
                    continue

                visited.add((n_r, n_c))
                stack.append((n_r, n_c))

        open_cells = (
            self.width * self.height
            - len(pattern_cells)
        )

        return len(visited) == open_cells

    def _all_corridors_connected(self) -> bool:
        """Check that every non-pattern cell is reachable."""

        start_c, start_r = self.entry
        start = (start_r, start_c)

        visited: set[Coordinate] = {start}
        stack: list[Coordinate] = [start]

        while stack:
            r, c = stack.pop()

            for neighbor in self._passage_neighbors(r, c):
                if neighbor in visited:
                    continue

                visited.add(neighbor)
                stack.append(neighbor)

        open_cells = (
            self.width * self.height
            - len(self.pattern_cells)
        )

        return len(visited) == open_cells

    def _walls_are_consistent(self) -> bool:
        """Check that neighboring cells agree about their shared walls."""

        for r in range(self.height):
            for c in range(self.width):

                if c + 1 < self.width:
                    east = bool(
                        self.grid[r][c].walls & 0b0010
                    )
                    west = bool(
                        self.grid[r][c + 1].walls & 0b1000
                    )

                    if east != west:
                        return False

                if r + 1 < self.height:
                    south = bool(
                        self.grid[r][c].walls & 0b0100
                    )
                    north = bool(
                        self.grid[r + 1][c].walls & 0b0001
                    )

                    if south != north:
                        return False

        return True

    def _borders_are_closed(self) -> bool:
        """Check that all external maze borders are closed."""

        for c in range(self.width):

            if not self.grid[0][c].walls & 0b0001:
                return False

            if not (
                self.grid[self.height - 1][c].walls
                & 0b0100
            ):
                return False

        for r in range(self.height):

            if not self.grid[r][0].walls & 0b1000:
                return False

            if not (
                self.grid[r][self.width - 1].walls
                & 0b0010
            ):
                return False

        return True

    def _validate_generated_maze(self) -> None:
        """Validate all maze-generation requirements."""

        if not self._walls_are_consistent():
            raise MazeError(
                "Maze walls are inconsistent"
            )

        if not self._borders_are_closed():
            raise MazeError(
                "Maze external borders must stay closed"
            )

        if not self._all_corridors_connected():
            raise MazeError(
                "Maze corridors are not fully connected"
            )

        for r, c in self.pattern_cells:
            if self.grid[r][c].walls != 0b1111:
                raise MazeError(
                    "42 pattern cells must stay fully closed"
                )

        if self._has_3x3_open_area():
            raise MazeError(
                "Maze contains a 3x3 open area"
            )

        loops = self._count_loops()

        if self.perfect and loops != 0:
            raise MazeError(
                "Perfect maze contains a loop"
            )

        if not self.perfect:

            if loops < 2:
                raise MazeError(
                    "Non-perfect maze needs at least "
                    "two independent loops"
                )

            if not self._has_two_entry_exit_routes():
                raise MazeError(
                    "Non-perfect maze needs more than "
                    "one entry-to-exit route"
                )

            required = self._required_non_perfect_cells()

            for r, c in required:
                if self._open_degree(r, c) < 2:
                    raise MazeError(
                        "Corners and centre must be open corridors"
                    )

    def get_grid(self) -> list[list[int]]:
        """Return the maze as integer wall values."""
        return [
            [
                self.grid[r][c].walls
                for c in range(self.width)
            ]
            for r in range(self.height)
        ]

    def solve(self) -> str:
        '''
        Return the shortest solution path from entry to exitt
        '''
        return MazeSolver.find_shortest_path(
            self.get_grid(),
            self.entry,
            self.exitt,
        )