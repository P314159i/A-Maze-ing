# A-Maze-ing project

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
