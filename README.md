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
