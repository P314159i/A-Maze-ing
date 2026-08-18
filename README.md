*This project has been created as part of the 42 curriculum by pamohamm, pidi.*

# A-Maze-ing

## Description

A-Maze-ing is a Python maze generator, solver, file exporter, and terminal visualizer.
The program reads a configuration file, generates either a perfect maze or a (playable) non-perfect maze, finds a shortest path from entry to exit, writes the maze using the required hexadecimal wall encoding, and displays it interactively in the terminal.

The maze contains a visible `42` pattern made from fully closed cells whenever the maze is large enough to place it without breaking connectivity.

## Instructions

### Requirements

- Python 3.10 or newer
- `pip`

Install the development dependencies:

```bash
make install
```

### Run

The required command is:

```bash
python3 a_maze_ing.py config.txt
```

or through the Makefile:

```bash
make run
```

To use a different configuration file:

```bash
make run CONFIG=path/to/config.txt
```

### Development commands

```bash
make debug        # run with pdb
make test         # run pytest
make lint         # run flake8 and mypy with the required flags
make lint-strict  # optional strict mypy check
make clean        # remove caches and build artifacts
```

### Build the reusable package

Install the standard Python build frontend if necessary:

```bash
python3 -m pip install build
```

Build the source distribution:

```bash
python3 -m build --sdist
```

The build tool writes the archive to `dist/`. For submission, copy the generated
`mazegen-*.tar.gz` file to the repository root:

```bash
cp dist/mazegen-*.tar.gz .
```

The package can then be installed with pip, for example:

```bash
python3 -m pip install ./mazegen-1.0.0.tar.gz
```

## Configuration file

The configuration file contains one `KEY=VALUE` pair per line. Empty lines and lines
starting with `#` are ignored.

Example:

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

### Supported keys

| Key | Required | Format | Description |
| --- | --- | --- | --- |
| `WIDTH` | Yes | positive integer | Maze width in cells |
| `HEIGHT` | Yes | positive integer | Maze height in cells |
| `ENTRY` | Yes | `x,y` | Entry coordinates inside the maze |
| `EXIT` | Yes | `x,y` | Exit coordinates inside the maze; must differ from `ENTRY` |
| `OUTPUT_FILE` | Yes | filename/path | File where the encoded maze is written |
| `PERFECT` | Yes | `True` or `False` | Selects perfect or non-perfect generation |
| `SEED` | No | integer | Makes generation reproducible |

Unknown keys, duplicate keys, malformed values, missing required keys, invalid
coordinates, and invalid dimensions are rejected with a clear configuration error.

## Maze generation algorithm

The generator uses a randomized depth-first search with backtracking. It starts from the
configured entry cell, repeatedly visits an unvisited neighbouring cell, opens the wall
between the two cells, and backtracks when no unvisited neighbour remains.

This algorithm was chosen because it naturally creates a connected spanning tree. That
makes it a direct fit for `PERFECT=True`, where the maze must contain no loops and
therefore has exactly one route between any two reachable corridor cells. A dedicated
`random.Random` instance allows the same seed and parameters to reproduce the same
maze.

Before carving, the generator reserves fully closed cells for the `42` pattern when a
safe placement exists. For `PERFECT=False`, additional passages are opened after the
base maze is generated. The generator validates that the resulting board stays
connected, avoids 3x3 open areas, contains at least two independent loops and multiple
entry-to-exit routes, and keeps the required corner and centre areas usable.

## Solver

`MazeSolver` uses breadth-first search (BFS) to find a shortest path from entry to exit.
The returned solution is a string made from `N`, `E`, `S`, and `W` directions.

## Output format

Each maze cell is written as one hexadecimal digit. Its four low bits represent closed
walls:

| Bit | Direction |
| --- | --- |
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

A set bit means the wall is closed; a cleared bit means it is open. Cells are written
row by row, with one maze row per line.

After an empty line, the output contains:

1. entry coordinates,
2. exit coordinates,
3. the shortest path as `N`, `E`, `S`, `W` characters.

## Terminal visualization

The curses-based terminal view displays the maze, entry, exit, and shortest path.

Controls:

- Arrow keys: scroll through large mazes
- `P`: show or hide the shortest path
- `A`: animate the shortest path
- `C`: change wall colour
- `V`: change solution-path colour
- `R`: generate a new maze with a random seed
- `S`: regenerate using the configured seed
- `Q`: quit

## Reusable `mazegen` package

The reusable part of the project is the maze generation and solving package under
`src/mazegen/`. After installation, its public API can be imported directly from
`mazegen`.

### Basic example

```python
from mazegen import Maze

maze = Maze(
    width=20,
    height=15,
    entry=(0, 0),
    exitt=(19, 14),
    perfect=True,
    myseed=42,
)

maze.generate()

grid = maze.get_grid()
solution = maze.solve()
```

`width` and `height` set the maze size. `myseed` controls reproducibility. `entry` and
`exitt` are `(x, y)` coordinates, and `perfect` selects the generation mode.

`get_grid()` returns the generated structure as a two-dimensional list of integer wall
values. `solve()` returns a shortest valid path as a string of direction characters.

## Team and project management

### Roles

- **Parvin Ghasemi** - primary work on configuration parsing, output handling, testing,
  integration, and visualizer improvements.
- **Parvin Diyanati** - primary work on maze generation, solving, interactive
  visualization, and integration.

Both members worked on integration, debugging, review, and final project compliance.

### Planning and evolution

The project began with separate work on parsing, maze generation, solving, and output.
As the modules were integrated, work shifted toward validating interactions between them,
meeting the perfect/non-perfect maze constraints, improving the terminal visualizer, and
adding regression tests. The final phase focused on edge cases, packaging, linting,
licensing, and documentation.

### What worked well

The modular structure made it possible to develop and test parsing, generation, solving,
output, and visualization independently before integrating them. Automated tests helped
catch regressions during later maze-generator and visualizer changes.

### What could be improved

Future work should integrate feature branches earlier, keep tests complete as each feature
is introduced, and maintain packaging and documentation continuously instead of leaving
them to the final phase.

### Tools used

- Git and GitHub for version control and collaboration
- pytest for automated tests
- flake8 for style checks
- mypy for static type checking
- Python `build` and setuptools for the reusable package
- `curses` for terminal visualization
- pdoc during development for inspecting generated API documentation

## Resources

### References

- Python data structures: https://docs.python.org/3/tutorial/datastructures.html
- Python `random`: https://docs.python.org/3/library/random.html
- Python `curses`: https://docs.python.org/3/library/curses.html
- Python packaging tutorial: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- pytest documentation: https://docs.pytest.org/
- flake8 documentation: https://flake8.pycqa.org/en/stable/
- mypy documentation: https://mypy.readthedocs.io/en/stable/

### Use of AI

AI tools, including ChatGPT, were used as development support for reviewing test coverage, checking edge cases, identifying packaging and subject-compliance issues, and improving docstrings and README wording. Suggested changes were reviewed against the project code and validated with the project's tests rather than accepted without verification.

## License

The reusable maze generator is distributed under the MIT License. See `LICENSE.md`.
