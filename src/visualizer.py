"""Terminal visualizer for the A-Maze-ing project."""

import curses

from src.mazegen.maze_generator import Maze


Coordinate = tuple[int, int]

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

COLOR_NAMES: tuple[str, ...] = (
    "white",
    "red",
    "green",
    "yellow",
    "cyan",
)


class TerminalVisualizer:
    """Display and interact with a maze in the terminal."""

    def __init__(self, maze: Maze) -> None:
        """Initialize the terminal visualizer."""
        self.maze = maze
        self.show_solution = False
        self.color_index = 0
        self.player: Coordinate = maze.entry
        self.message = ""

    def run(self) -> None:
        """Run the terminal visualizer."""
        curses.wrapper(self._curses_loop)

    def _curses_loop(self, screen: curses.window) -> None:
        """Handle drawing and keyboard controls."""

        try:
            curses.curs_set(0)
        except curses.error:
            pass

        screen.keypad(True)

        self._setup_colors()

        while True:
            self._draw_curses(screen)

            key = screen.getch()

            if key in (ord("q"), ord("Q")):
                break

            if key in (
                ord("w"),
                ord("W"),
                curses.KEY_UP,
            ):
                self._move_player("w")

            elif key in (
                ord("a"),
                ord("A"),
                curses.KEY_LEFT,
            ):
                self._move_player("a")

            elif key in (
                ord("s"),
                ord("S"),
                curses.KEY_DOWN,
            ):
                self._move_player("s")

            elif key in (
                ord("d"),
                ord("D"),
                curses.KEY_RIGHT,
            ):
                self._move_player("d")

            elif key in (ord("p"), ord("P")):
                self.show_solution = not self.show_solution
                self.message = ""

            elif key in (ord("c"), ord("C")):
                self.color_index = (
                    self.color_index + 1
                ) % len(COLOR_NAMES)
                self.message = ""

            elif key in (ord("r"), ord("R")):
                self.maze.myseed = None
                self.maze.generate()

                self.player = self.maze.entry
                self.message = "New maze generated."

    def _setup_colors(self) -> None:
        """Initialize curses wall colors."""

        if not curses.has_colors():
            return

        curses.start_color()

        try:
            curses.use_default_colors()
            background = -1
        except curses.error:
            background = curses.COLOR_BLACK

        colors = (
            curses.COLOR_WHITE,
            curses.COLOR_RED,
            curses.COLOR_GREEN,
            curses.COLOR_YELLOW,
            curses.COLOR_BLUE,
            curses.COLOR_CYAN,
        )

        for pair_number, color in enumerate(
            colors,
            start=1,
        ):
            try:
                curses.init_pair(
                    pair_number,
                    color,
                    background,
                )
            except curses.error:
                pass

    def _wall_color(self) -> int:
        """Return the currently selected wall color."""

        if not curses.has_colors():
            return curses.A_NORMAL

        return curses.color_pair(
            self.color_index + 1
        )

    def _solution_cells(self) -> set[Coordinate]:
        """Return all cells in the shortest solution path."""

        if not self.show_solution:
            return set()

        solution = self.maze.solve()

        x, y = self.maze.entry
        cells: set[Coordinate] = {(x, y)}

        moves: dict[str, tuple[int, int]] = {
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
        """Return the symbol shown inside a cell."""

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
        """Move the player if no wall blocks the movement."""

        x, y = self.player

        grid = self.maze.get_grid()
        walls = grid[y][x]

        moves: dict[str, tuple[int, int, int]] = {
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

    def _draw_curses(
            self,
            screen: curses.window,
            ) -> None:
        """Draw the maze and scroll automatically with the player."""

        screen.erase()
        screen.refresh()

        screen_height, screen_width = screen.getmaxyx()

        if screen_height < 4 or screen_width < 5:
            return

        # Two extra rows/columns prevent curses from writing
        # exactly into the bottom-right corner.
        pad_height = self.maze.height * 2 + 2
        pad_width = self.maze.width * 4 + 2

        pad = curses.newpad(
            pad_height,
            pad_width,
        )

        grid = self.maze.get_grid()
        solution_cells = self._solution_cells()
        wall_color = self._wall_color()

        # Draw every maze row.
        for y in range(self.maze.height):
            top_row = y * 2
            middle_row = top_row + 1

            for x in range(self.maze.width):
                column = x * 4
                walls = grid[y][x]

                pad.addstr(
                    top_row,
                    column,
                    "+",
                    wall_color,
                )

                if walls & NORTH:
                    pad.addstr(
                        top_row,
                        column + 1,
                        "---",
                        wall_color,
                    )

                if walls & WEST:
                    pad.addstr(
                        middle_row,
                        column,
                        "|",
                        wall_color,
                    )

                symbol = self._cell_symbol(
                    x,
                    y,
                    solution_cells,
                )

                pad.addstr(
                    middle_row,
                    column + 1,
                    f" {symbol} ",
                )

            # Right wall of the final cell.
            final_column = self.maze.width * 4

            pad.addstr(
                top_row,
                final_column,
                "+",
                wall_color,
            )

            last_cell = grid[y][self.maze.width - 1]

            if last_cell & EAST:
                pad.addstr(
                    middle_row,
                    final_column,
                    "|",
                    wall_color,
                )

        # Draw bottom border.
        bottom_row = self.maze.height * 2

        for x in range(self.maze.width):
            column = x * 4

            pad.addstr(
                bottom_row,
                column,
                "+",
                wall_color,
            )

            if grid[self.maze.height - 1][x] & SOUTH:
                pad.addstr(
                    bottom_row,
                    column + 1,
                    "---",
                    wall_color,
                )

        pad.addstr(
            bottom_row,
            self.maze.width * 4,
            "+",
            wall_color,
        )

        # Leave two terminal lines for controls.
        view_height = screen_height - 2
        view_width = screen_width

        player_x, player_y = self.player

        # Player position inside the big pad.
        player_pad_y = player_y * 2 + 1
        player_pad_x = player_x * 4 + 2

        # Try to keep the player in the middle of the screen.
        scroll_y = max(
            0,
            player_pad_y - view_height // 2,
        )

        scroll_x = max(
            0,
            player_pad_x - view_width // 2,
        )

        # Do not scroll past the maze.
        max_scroll_y = max(
            0,
            pad_height - view_height,
        )

        max_scroll_x = max(
            0,
            pad_width - view_width,
        )

        scroll_y = min(scroll_y, max_scroll_y)
        scroll_x = min(scroll_x, max_scroll_x)

        # How much of the pad can actually be displayed.
        rows_to_show = min(
            view_height,
            pad_height - scroll_y,
        )

        columns_to_show = min(
            view_width,
            pad_width - scroll_x,
        )

        if rows_to_show > 0 and columns_to_show > 0:
            pad.refresh(
                scroll_y,
                scroll_x,
                0,
                0,
                rows_to_show - 1,
                columns_to_show - 1,
            )

        # Bottom controls.
        controls = (
            "WASD/arrows move | "
            "P path | R regenerate | "
            "C color | Q quit"
        )

        status = f"Color: {COLOR_NAMES[self.color_index]}"

        if self.message:
            status += f" | {self.message}"

        try:
            screen.addnstr(
                screen_height - 2,
                0,
                controls,
                screen_width - 1,
            )

            screen.addnstr(
                screen_height - 1,
                0,
                status,
                screen_width - 1,
            )

            screen.refresh()

        except curses.error:
            pass