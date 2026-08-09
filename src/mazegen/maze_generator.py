import random

# from src.solver import MazeSolver


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
            exit: tuple[int, int],
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

        if exit is not None:
            self.exit = exit
        else:
            self.exit = (width - 1, height - 1)

        if not (
            0 <= self.entry[0] < width
            and 0 <= self.entry[1] < height
        ):
            raise ValueError("Entry is outside the maze")

        if not (
            0 <= self.exit[0] < width
            and 0 <= self.exit[1] < height
        ):
            raise ValueError("Exit is outside the maze")

        if self.entry == self.exit:
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

        self.grid: list[list["Maze.Cell"]] = [
            [self.Cell(x, y) for y in range(height)]
            for x in range(width)
        ]

    def reset(self) -> None:
        for column in self.grid:
            for cell in column:
                cell.walls = 0b1111
                cell.visited = False

    def generate(self) -> None:
        self.reset()
        self.rndm.seed(self.myseed)

        start_r, start_c = self.entry
        self.grid[start_r][start_c].visited = True

        stack: list["Maze.Cell"] = [
            self.grid[start_r][start_c]
        ]

        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0)
        ]

        while stack:
            current = stack[-1]
            neighbors: list["Maze.Cell"] = []

            for d_r, d_c in directions:
                n_r = current.r + d_r
                n_c = current.c + d_c

                if (
                    0 <= n_r < self.width
                    and 0 <= n_c < self.height
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

                if next_cell.c > current.c:
                    current.walls &= 0b1011
                    next_cell.walls &= 0b1110

                elif next_cell.c < current.c:
                    current.walls &= 0b1110
                    next_cell.walls &= 0b1011

                elif next_cell.r > current.r:
                    current.walls &= 0b1101
                    next_cell.walls &= 0b0111

                elif next_cell.r < current.r:
                    current.walls &= 0b0111
                    next_cell.walls &= 0b1101

                next_cell.visited = True
                stack.append(next_cell)

            else:
                stack.pop()

            if self.perfect:
                return
            else:
                self._make_non_perfect()

    def make_non_perfect(self) -> None:

        dead_ends: list[tuple[int, int]] = []

        for x in range(self.width):
            for y in range(self.height):
                cell = self.grid[x][y]

            if cell.walls.bit_count() == 3:
                dead_ends.append((x, y))
        self.rndm.shuffle(dead_ends)

        for x, y in dead_ends:
            cell = self.grid[x][y]

            possible_walls: list[tuple[int, int]] = []

            if y > 0 and cell.walls & 0b0001:
                possible_walls.append((x, y - 1))

            if x < self.width - 1 and cell.walls & 0b0010:
                possible_walls.append((x + 1, y))

            if y < self.height - 1 and cell.walls & 0b0100:
                possible_walls.append((x, y + 1))

            if x > 0 and cell.walls & 0b1000:
                possible_walls.append((x - 1, y))

            if possible_walls:
                nx, ny = self.rndm.choice(possible_walls)
                self._open_wall(x, y, nx, ny)

    # it returns only one cell's wall integer 0-15
    # solver needs a 2D list of integers accessed as maze[x][y]
    def get_grid(self) -> list[list[int]]:
        return [
            [
                self.grid[x][y].walls
                for x in range(self.width)
            ]
            for y in range(self.height)
        ]

    # def solve(self) -> str:
    #     """Return the shortest solution path from entry to exit."""
    #     return MazeSolver.find_shortest_path(
    #         self.get_grid(),
    #         self.entry,
    #         self.exit,
    #     )

    # todo: check perfect