## Hashiwokakero Solver

A Constraint Programming solver for the [Hashiwokakero](https://en.wikipedia.org/wiki/Hashiwokakero) logic puzzle, made with Google OR-Tools.

It includes two versions :

- The _basic solver_ takes the digit of each island as input to solve the grid (.has files).
- The _probabilistic solver_ is meant to correct errors from an image recognition system that reads Hashi grids from images. It requires a list of probabilities for each island :

  | Island | x_position | y_position | 1   | 2   | 3   | 4   | 5   | 6   | 7   | 8   |
  | ------ | ---------- | ---------- | --- | --- | --- | --- | --- | --- | --- | --- |
  | 1      | 0          | 2          | 2%  | 1%  | 87% | 0%  | 0%  | 0%  | 0%  | 10% |
  | ...    |            |            |     |     |     |     |     |     |     |     |

  It finds the grid that has a solution with the highest probabilities. 
  With the --solution-is-unique argument, if that grid gives multiple solutions, it solves the next most likely grid, and repeats until it finds one with a unique solution.

### Testing

- Install requirements `pip install -r requirements.txt`
- Run `python basic_solver.py puzzles/basic/100/Hs_16_100_25_00_001.has` to try the basic solver \
  or `python probabilistic_solver.py puzzles/probabilistic/toy_grid_probs.json` to try the probabilistic one. Add --solution-is-unique to specify that the grid has a unique solution.

Puzzles in `puzzles/basic/[1-4]00` are from [Coelho et al. 2019](https://arxiv.org/abs/1905.00973). They allow multiple solutions.  
Run `python create_probs_grids_from_has_files.py` to create probabilistic grids from the .has files in puzzles/basic/
