import random

from .solver import MazeSolver


class Maze:
    '''
    nested class Cell is part of the Maze
    so Maze takes attributes from Cell
    to make grid of cells
    '''
    class Cell:
        def __init__(
                self,
                r: int,
                c: int,
                walls: int = 0b1111,
                visited: bool = False
                ) -> None:
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

        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be positive")

        self.width = width
        self.height = height
        self.myseed = myseed
        self.rndm = random.Random(myseed)
        self.entry = entry
        self.perfect = perfect
        self.exitt = exitt

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

        '''
        assign an enter and exit
        entry = starting cell for DFS
        exit = destination cell for player
        DFS carves the entire Maze starting from entry

        exit and enter: "any" cell with "valid coordinate" and "in the maze"

        Maze.Cell is written in commas cuz Maze is still being defined
        and MAze.Cell is kept in delay as string & later it's accessed
        '''

        # grid[row][column]
        self.grid: list[list["Maze.Cell"]] = [
            [self.Cell(r, c) for c in range(width)]
            for r in range(height)
        ]

    def reset(self) -> None:
        for row in self.grid:
            for cell in row:
                cell.walls = 0b1111
                cell.visited = False

    def generate(self) -> None:
        self.reset()
        self.rndm.seed(self.myseed)

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
                    and not self.grid[n_r][n_c].visited
                ):
                    neighbors.append(
                        self.grid[n_r][n_c]
                    )

            if neighbors:
                next_cell = self.rndm.choice(neighbors)

                '''
                *DFS*
                Walls are stored as 4 bit binary.
                Bit 0 = north
                Bit 1 = east
                Bit 2 = south
                Bit 3 = west

                Binary Mask =
                north: 0b1110
                east:  0b1101
                south: 0b1011
                west:  0b0111
                '''

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

    def make_non_perfect(self) -> None:

        dead_ends: list[tuple[int, int]] = []

        for r in range(self.height):
            for c in range(self.width):
                cell = self.grid[r][c]

                if cell.walls.bit_count() == 3:
                    dead_ends.append((r, c))

        self.rndm.shuffle(dead_ends)

        for r, c in dead_ends:
            cell = self.grid[r][c]

            possible_walls: list[tuple[int, int]] = []

            if r > 0 and cell.walls & 0b0001:
                possible_walls.append((r - 1, c))

            if c < self.width - 1 and cell.walls & 0b0010:
                possible_walls.append((r, c + 1))

            if r < self.height - 1 and cell.walls & 0b0100:
                possible_walls.append((r + 1, c))

            if c > 0 and cell.walls & 0b1000:
                possible_walls.append((r, c - 1))

            if possible_walls:
                n_r, n_c = self.rndm.choice(possible_walls)
                self._open_wall(r, c, n_r, n_c)

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

    def get_grid(self) -> list[list[int]]:
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
