# A-Maze-ing project
# README.md for class Maze of maze-generator.py

here goes the rest


## To Run:
python a_maze_ing.py config.txt > result.txt 2> errors.txt
python a_maze_ing.py config.txt 2> errors.txt   # 2 is for stderr
python a_maze_ing.py config.txt > result.txt    # 1 is for stdout

#### here's an example:
```
print("Maze generated")
print("Bad configuration", file=sys.stderr)
```
then:
Maze generated goes into result.txt
Bad configuration still appears in the terminal
That is useful because errors do not get mixed into normal program output.


## Tests
python -m pytest
python -m pytest -v
python -m pytest -vv

python -m unittest discover -s tests
python -m unittest discover -s tests -v

## Reusable Maze Generator

the Maze class is the reusable part of the project.
it creates the grid, generates the maze using DFS,
gives access to the maze wall values, and gives access
to the shortest solution through the solver.

### make a Maze

first instantiate the class:

```python
maze = Maze(
    width=20,
    height=15,
    myseed=42,
    entry=(0, 0),
    exit=(19, 14)
)
````

width + height = size of maze

myseed = random seed
same seed + same settings = same generated maze

entry = starting coordinate
exit = destination coordinate

### generate maze

```python
maze.generate()
```

generate() uses DFS to carve the maze.

### get maze structure

```python
grid = maze.get_grid()
```

grid is a 2D list of wall integers from 0-15.

order starts top-left, goes row by row,
and ends bottom-right.

access a cell with:

```python
grid[y][x]
```

### get solution

```python
solution = maze.solve()
```

solve() sends:

* grid
* entry
* exit

to MazeSolver.find_shortest_path()

solver uses BFS and returns the shortest path
as N, E, S, W characters.

```

This covers the specific documentation points required in Chapter VI. :contentReference[oaicite:1]{index=1}
```


** * `__init__.py` makes a folder behave like one Python package and can expose selected names cleanly.

* We group files in `mazegen/` to keep the reusable package in one folder, and to make __init__ inside of it, so that we can first refer to the folder in .toml file to make the package isntead of seperately, but more importantly when wanting to re-use the class Maze, instead of importing files and classes like:

	from maze_generator import Maze
	from solver import MazeSolver
just import:
	from mazegen import Maze
which imports mazegen (both files) then uses Maze class





pyproject.toml is a configuration file that different tools read when you run those tools.

For your file:

python3 -m build reads [build-system] and [project].
pytest reads [tool.pytest.ini_options].
mypy reads [tool.mypy].
flake8 normally does not read [tool.flake8] unless extra support is added.




the subject tells us several things the evaluator may check, but not the exact evaluation sheet.

They can:

run your program with config files;
inspect the generated output;
use maze_analyzer.py / Moulinette to check wall consistency, PERFECT=True, and playable non-perfect mazes;
ask you to explain your code and decisions; the subject explicitly warns that not understanding your own code can fail the evaluation;
ask for a small live modification, such as changing a function, display, or data structure within a few minutes.
evaluate only what is actually committed in your Git repository.


for building the standalone package run:
	python3 -m pip install build
	python3 -m build --sdist
  it automatically puts the .tar.gz inside a "dist" folder, you should copy it to the root.


.
