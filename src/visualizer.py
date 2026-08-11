"""Interactive terminal visualization for generated and solved mazes."""

import curses

from src.mazegen.maze_generator import Maze


Coordinate = tuple[int, int]

NORTH = 0b0001
EAST = 0b0010
SOUTH = 0b0100
WEST = 0b1000

WALL = "█"
HORIZONTAL_WALL = WALL * 3
PATTERN_FILL = "▓" * 3

COLOR_NAMES: tuple[str, ...] = (
    "white",
    "red",
    "green",
    "yellow",
    "blue",
    "cyan",
)


class TerminalVisualizer:
    """Display a maze and its shortest solution in a curses terminal."""

    def __init__(
        self,
        maze: Maze,
        solved_path: str | None = None,
    ) -> None:
        """Initialize the visualizer with the solution visible."""
        self.maze = maze
        self.configured_seed = maze.myseed
        self.solved_path = (
            maze.solve() if solved_path is None else solved_path
        )
        self.show_solution = True
        self.solution_step_limit: int | None = None
        self.color_index = 0
        self.solution_color_index = 2
        self.scroll_x = 0
        self.scroll_y = 0
        self.message = "Shortest path shown."

    def run(self) -> None:
        """Open the interactive terminal visualization."""
        curses.wrapper(self._curses_loop)

    def _curses_loop(self, screen: curses.window) -> None:
        """Draw the maze and process visualization controls."""
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
                return

            if key == curses.KEY_UP:
                self.scroll_y = max(0, self.scroll_y - 2)
            elif key == curses.KEY_DOWN:
                self.scroll_y += 2
            elif key == curses.KEY_LEFT:
                self.scroll_x = max(0, self.scroll_x - 4)
            elif key == curses.KEY_RIGHT:
                self.scroll_x += 4
            elif key in (ord("p"), ord("P")):
                self.solution_step_limit = None
                self.show_solution = not self.show_solution
                state = "shown" if self.show_solution else "hidden"
                self.message = f"Shortest path {state}."
            elif key in (ord("a"), ord("A")):
                if self._animate_solution(screen):
                    return
            elif key in (ord("c"), ord("C")):
                self.color_index = (
                    self.color_index + 1
                ) % len(COLOR_NAMES)
                self.message = (
                    f"Wall color: {COLOR_NAMES[self.color_index]}."
                )
            elif key in (ord("v"), ord("V")):
                self.solution_color_index = (
                    self.solution_color_index + 1
                ) % len(COLOR_NAMES)
                self.message = (
                    "Solution color: "
                    f"{COLOR_NAMES[self.solution_color_index]}."
                )
            elif key in (ord("r"), ord("R")):
                self._regenerate(use_configured_seed=False)
            elif key in (ord("s"), ord("S")):
                if self.configured_seed is None:
                    self.message = "No seed was configured."
                else:
                    self._regenerate(use_configured_seed=True)

    def _regenerate(self, use_configured_seed: bool) -> None:
        """Generate a maze and refresh the path shown by the solver."""
        self.maze.myseed = (
            self.configured_seed if use_configured_seed else None
        )
        self.maze.generate()
        self.solved_path = self.maze.solve()
        self.scroll_x = 0
        self.scroll_y = 0
        self.show_solution = True
        self.solution_step_limit = None

        if use_configured_seed:
            self.message = (
                f"Seed {self.configured_seed} replayed; "
                "shortest path shown."
            )
        else:
            self.message = "New random maze; shortest path shown."

    def _animate_solution(self, screen: curses.window) -> bool:
        """Animate the solver path and report whether quit was pressed."""
        self.show_solution = True
        self.message = "Animating solution; press any key to skip."
        quit_requested = False
        screen.nodelay(True)

        try:
            for step in range(len(self.solved_path) + 1):
                self.solution_step_limit = step
                self._draw_curses(screen)

                key = screen.getch()
                if key != -1:
                    quit_requested = key in (ord("q"), ord("Q"))
                    break

                curses.napms(45)
        finally:
            screen.nodelay(False)
            self.solution_step_limit = None

        self.message = "Solution animation complete."
        return quit_requested

    def _setup_colors(self) -> None:
        """Initialize every selectable wall color."""
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

        for pair_number, color in enumerate(colors, start=1):
            try:
                curses.init_pair(pair_number, color, background)
            except curses.error:
                pass

    def _wall_color(self) -> int:
        """Return the currently selected curses wall style."""
        if not curses.has_colors():
            return curses.A_NORMAL

        return curses.color_pair(self.color_index + 1)

    def _solution_color(self) -> int:
        """Return the currently selected solution-path style."""
        if not curses.has_colors():
            return curses.A_BOLD

        return curses.color_pair(self.solution_color_index + 1)

    def _solution_cells(self) -> set[Coordinate]:
        """Return the cells crossed by the shortest solution path."""
        if not self.show_solution:
            return set()

        x, y = self.maze.entry
        cells: set[Coordinate] = {(x, y)}
        moves: dict[str, Coordinate] = {
            "N": (0, -1),
            "E": (1, 0),
            "S": (0, 1),
            "W": (-1, 0),
        }

        for step, direction in enumerate(self.solved_path, start=1):
            if (
                self.solution_step_limit is not None
                and step > self.solution_step_limit
            ):
                break

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
        if (x, y) == self.maze.entry:
            return "E"
        if (x, y) == self.maze.exitt:
            return "X"
        if (y, x) in self.maze.pattern_cells:
            return "#"
        if (x, y) in solution_cells:
            return "*"
        return " "

    @staticmethod
    def _safe_addstr(
        window: curses.window,
        y: int,
        x: int,
        text: str,
        style: int = curses.A_NORMAL,
    ) -> None:
        """Write to a curses window while tolerating edge clipping."""
        try:
            window.addstr(y, x, text, style)
        except curses.error:
            pass

    def _draw_maze(self, pad: curses.window) -> None:
        """Draw all walls and cell symbols onto a curses pad."""
        grid = self.maze.get_grid()
        solution_cells = self._solution_cells()
        wall_color = self._wall_color()
        solution_color = self._solution_color()

        for y in range(self.maze.height):
            top_row = y * 2
            middle_row = top_row + 1

            for x in range(self.maze.width):
                column = x * 4
                walls = grid[y][x]

                self._safe_addstr(pad, top_row, column, WALL, wall_color)
                if walls & NORTH:
                    self._safe_addstr(
                        pad,
                        top_row,
                        column + 1,
                        HORIZONTAL_WALL,
                        wall_color,
                    )
                if walls & WEST:
                    self._safe_addstr(
                        pad, middle_row, column, WALL, wall_color
                    )

                symbol = self._cell_symbol(x, y, solution_cells)
                cell_contents = (
                    PATTERN_FILL
                    if (y, x) in self.maze.pattern_cells
                    else f" {symbol} "
                )
                cell_style = (
                    solution_color
                    if (
                        (x, y) in solution_cells
                        and (x, y) not in (
                            self.maze.entry,
                            self.maze.exitt,
                        )
                    )
                    else curses.A_NORMAL
                )
                self._safe_addstr(
                    pad,
                    middle_row,
                    column + 1,
                    cell_contents,
                    cell_style,
                )

            final_column = self.maze.width * 4
            self._safe_addstr(
                pad, top_row, final_column, WALL, wall_color
            )
            if grid[y][self.maze.width - 1] & EAST:
                self._safe_addstr(
                    pad, middle_row, final_column, WALL, wall_color
                )

        bottom_row = self.maze.height * 2
        for x in range(self.maze.width):
            column = x * 4
            self._safe_addstr(
                pad, bottom_row, column, WALL, wall_color
            )
            if grid[self.maze.height - 1][x] & SOUTH:
                self._safe_addstr(
                    pad,
                    bottom_row,
                    column + 1,
                    HORIZONTAL_WALL,
                    wall_color,
                )

        self._safe_addstr(
            pad,
            bottom_row,
            self.maze.width * 4,
            WALL,
            wall_color,
        )

    def _draw_curses(self, screen: curses.window) -> None:
        """Draw a scrollable maze plus its legend and controls."""
        screen.erase()
        screen_height, screen_width = screen.getmaxyx()

        if screen_height < 6 or screen_width < 20:
            self._safe_addstr(screen, 0, 0, "Terminal is too small.")
            screen.refresh()
            return

        pad_height = self.maze.height * 2 + 2
        pad_width = self.maze.width * 4 + 2
        pad = curses.newpad(pad_height, pad_width)
        self._draw_maze(pad)

        view_height = screen_height - 3
        view_width = screen_width
        max_scroll_y = max(0, pad_height - view_height)
        max_scroll_x = max(0, pad_width - view_width)
        self.scroll_y = min(self.scroll_y, max_scroll_y)
        self.scroll_x = min(self.scroll_x, max_scroll_x)

        rows_to_show = min(view_height, pad_height - self.scroll_y)
        columns_to_show = min(view_width, pad_width - self.scroll_x)

        legend = "E entry | X exit | * shortest path | ▓ closed 42 cell"
        controls = (
            "Arrows | P path | A animate | R new | S seed | "
            "C walls | V path | Q quit"
        )
        status = (
            f"Walls: {COLOR_NAMES[self.color_index]} | "
            f"Path: {COLOR_NAMES[self.solution_color_index]} | "
            f"{self.message}"
        )

        try:
            if rows_to_show > 0 and columns_to_show > 0:
                pad.overwrite(
                    screen,
                    self.scroll_y,
                    self.scroll_x,
                    0,
                    0,
                    rows_to_show - 1,
                    columns_to_show - 1,
                )

            screen.addnstr(
                screen_height - 3, 0, legend, screen_width - 1
            )
            screen.addnstr(
                screen_height - 2, 0, controls, screen_width - 1
            )
            screen.addnstr(
                screen_height - 1, 0, status, screen_width - 1
            )
            screen.refresh()
        except curses.error:
            pass
