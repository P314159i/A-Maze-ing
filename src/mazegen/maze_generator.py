import random

from src.solver import MazeSolver


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
            myseed: int | None = None,
            entry: tuple[int, int] = (0, 0),
            exit: tuple[int, int] | None = None
            ) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("Maze dimensions must be positive")

        self.width = width
        self.height = height
        self.myseed = myseed
        self.rndm = random.Random(myseed)
        self.entry = entry

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

    def solve(self) -> str:
        """Return the shortest solution path from entry to exit."""
        return MazeSolver.find_shortest_path(
            self.get_grid(),
            self.entry,
            self.exit,
        )

    # do your own tests, put them in "test" folder, naming (test_...)

    '''
    A-Maze-ing main() -> accesses to "class Maze" and instantiate a maze)
    ↓
    MazeSolver.find_shortest_path(...)

    ** in main() :
        grid = maze.get_grid()

        solution = MazeSolver.find_shortest_path(
            grid,
            maze.entry,
            maze.exit,
        )

    OR now, because Maze has a public solve() method:

        solution = maze.solve()

    ** solver gets:
        MazeSolver.find_shortest_path(
            maze,         # list[list[int]]
            entry_point,  # tuple[int, int]
            exit_point,   # tuple[int, int]
        )

        and inside solver:
            maze[y][x]

        This all comes from main, after instantiating maze class


        ** so:

        main()
            ↓
            create Maze(...)
                ↓
                maze.generate()
                    ↓
                    get:
                    - whole maze grid / cell wall integers
                    - entry
                    - exit
                        ↓
                        pass those 3 to MazeSolver
                            ↓
                            solver returns solution string like "EESSWN..."

    Width and height do not need to be passed separately
        because her solver calculates them from the grid itself using
        len(maze) and len(maze[0]).

    access Maze Class from main() as:
        - maze.generate()
        - solution = maze.solve()
        then maze.solve() of class Maze calls get_grid() and passes the grid 
            to BFS solver, aka MazeSolver.find_shortest_path(...)

    '''
