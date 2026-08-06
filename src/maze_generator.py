import random


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
        stack: list["Maze.Cell"] = [self.grid[start_r][start_c]]
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

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
                    neighbors.append(self.grid[n_r][n_c])

            if neighbors:
                next_cell = self.rndm.choice(neighbors)
                '''
                *DFS*
                Walls are stored as 4 bit binary: NESW (0bxxxx)
                Binary Mask = north:0b0111,east:0b1011,south:0b1101,west:0b1110
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

    # def get_cell(self, r: int, c: int) -> Cell:
    #     return self.grid[r][c]
        '''
        to do next:
        custom parameters such as size and seed;
        the generated maze structure;
        at least one solution path;
        documentation showing how to instantiate and use it;
        packaging as a standalone installable module.

        seed
        entry
        exit
        solution path
        public access methods
        
        BFS needs entrance and exit of the maze
        entry=(2, 3)
        '''