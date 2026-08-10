"""Terminal visualizer for the A-Maze-ing project."""

from src.mazegen.maze_generator import Maze


Coordinate = tuple[int, int]

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

RESET = "\033[0m"

WALL_COLORS: tuple[tuple[str, str], ...] = (
    ("white", "\033[37m"),
    ("red", "\033[31m"),
    ("green", "\033[32m"),
    ("yellow", "\033[33m"),
    ("blue", "\033[34m"),
    ("cyan", "\033[36m"),
)

class TerminalVisualizer:
    """Display and interact with a maze in the terminal."""

    def __init__(self, maze: Maze) -> None:
        """Initialize the terminal visualizer."""
        self.maze = maze
        self.show_solution = True
        self.color_index = 0
        self.player: Coordinate = maze.entry
        self.message = ""

    def _wall(self, text: str) -> str:
        """Return wall text using the current wall color."""
        color = WALL_COLORS[self.color_index][1]
        return f"{color}{text}{RESET}"

    def _solution_cells(self) -> set[Coordinate]:
        """Return all cells belonging to the shortest solution path."""
        if not self.show_solution:
            return set()

        solution = self.maze.solve()

        x, y = self.maze.entry
        cells: set[Coordinate] = {(x, y)}

        moves = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        for direction in solution:
            dx, dy = moves[direction]
            x += dx
            y += dy
            cells.add((x, y))

        return cells

    def _cell_symbol(
            self,
            x: int,
            y: int,
            solution_cells: set[Coordinate],
            ) -> str:
        """Return the symbol displayed inside one maze cell."""

        if (x, y) == self.player:
            return "@"

        if (x, y) == self.maze.entry:
            return "E"

        if (x, y) == self.maze.exitt:
            return "X"

        if (y, x) in self.maze.pattern_cells:
            return "#"

        if (x, y) in solution_cells:
            return "*"

        return " "

    def _move_player(self, direction: str) -> None:
        """Move the player if there is no wall blocking the move."""

        x, y = self.player
        walls = self.maze.get_grid()[y][x]

        moves = {
            "w": (0, -1, NORTH),
            "d": (1, 0, EAST),
            "s": (0, 1, SOUTH),
            "a": (-1, 0, WEST),
        }

        dx, dy, wall_bit = moves[direction]

        if walls & wall_bit:
            self.message = "You hit a wall."
            return

        new_x = x + dx
        new_y = y + dy

        if not (
            0 <= new_x < self.maze.width
            and 0 <= new_y < self.maze.height
        ):
            self.message = "You cannot leave the maze."
            return

        if (new_y, new_x) in self.maze.pattern_cells:
            self.message = "The 42 pattern blocks this cell."
            return

        self.player = (new_x, new_y)
        self.message = ""

        if self.player == self.maze.exitt:
            self.message = "You reached the exit!"

    def display(self) -> None:
        """Draw the current maze in the terminal."""

        print("\033[2J\033[H", end="")

        grid = self.maze.get_grid()
        solution_cells = self._solution_cells()

        for y in range(self.maze.height):
            top = ""
            middle = ""

            for x in range(self.maze.width):
                walls = grid[y][x]

                top += self._wall("+")

                if walls & NORTH:
                    top += self._wall("---")
                else:
                    top += "   "

                if walls & WEST:
                    middle += self._wall("|")
                else:
                    middle += " "

                symbol = self._cell_symbol(
                    x,
                    y,
                    solution_cells,
                )

                middle += f" {symbol} "

            top += self._wall("+")

            last_cell = grid[y][self.maze.width - 1]

            if last_cell & EAST:
                middle += self._wall("|")
            else:
                middle += " "

            print(top)
            print(middle)

        bottom = ""

        for x in range(self.maze.width):
            bottom += self._wall("+")

            if grid[self.maze.height - 1][x] & SOUTH:
                bottom += self._wall("---")
            else:
                bottom += "   "

        bottom += self._wall("+")
        print(bottom)

        color_name = WALL_COLORS[self.color_index][0]

        print()
        print("@ = player")
        print("E = entry")
        print("X = exit")
        print("# = 42")
        print("* = shortest path")
        print(f"Wall color: {color_name}")

        if self.message:
            print(self.message)

    def run(self) -> None:
        """Run the terminal visualization controls."""

        while True:
            self.display()

            print()
            print("[W] Move north")
            print("[A] Move west")
            print("[S] Move south")
            print("[D] Move east")
            print("[R] Regenerate maze")
            print("[P] Show/hide solution")
            print("[C] Change wall color")
            print("[Q] Quit")

            choice = input("> ").strip().lower()

            if choice == "q":
                break

            if choice in {"w", "a", "s", "d"}:
                self._move_player(choice)

            elif choice == "p":
                self.show_solution = not self.show_solution

            elif choice == "c":
                self.color_index = (
                    self.color_index + 1
                ) % len(WALL_COLORS)

            elif choice == "r":
                self.maze.myseed = None
                self.maze.generate()
                self.player = self.maze.entry
                self.message = "New maze generated."