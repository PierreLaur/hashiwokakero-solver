import sys
import pandas as pd
from ortools.sat.python import cp_model
import numpy as np

class HashiGrid :
    def __init__(self, width, height, n_islands) -> None:
        self.width = width
        self.height = height

        self.n_islands = n_islands

        self.island_coordinates = []
        self.digits = []

    def fill_grid(self,grid) :
        for i,line in enumerate(grid) :
            for j,square in enumerate(line) :
                if square != 0 :
                    self.island_coordinates.append(
                        (i,j)
                    )
                    self.digits.append(square)

    def print_grid (self) :
        for coords, d in zip(self.island_coordinates, self.digits) :
            print(f'Island {coords}    with n_bridges = {d}')

def read_has_file(file) :
    file = sys.argv[1]
    grid = []
    with open(file) as f :
        width, height, n_islands = f.readline().split()
        for line in f :
            grid.append(list(map(lambda x : int(x), line.strip().split())))

    h_grid = HashiGrid(width, height, int(n_islands))
    h_grid.fill_grid(grid)
    
    return h_grid

class ProbabilisticHashiGrid :
    def __init__(self, width, height, n_islands) -> None:
        self.width = width
        self.height = height
        self.n_islands = n_islands

        self.island_coordinates = []

        self.probs = {}
        self.digits = {}
        self.potential_digit_combinations = []

    def fill_grid(self, grid_df, model) :
        for l in range(self.n_islands) :
            island_coords = (grid_df.loc[l+1,'row'],grid_df.loc[l+1,'col'])
            self.island_coordinates.append(island_coords)
            self.probs[l] = [i for i in grid_df.loc[l+1,'1_prob':'8_prob']]

    def set_digits(self) :
        for l in range(self.n_islands) :
            self.digits[l] = np.argmax(self.probs[l])+1

    # def eliminate_combination

    def print_grid (self) :
        for coords, d in zip(self.island_coordinates, self.digits) :
            print(f'Island {coords}    with n_bridges = {d}')
    
def read_grid_as_df(file) :
    grid_df = pd.read_csv(file)
    grid_df.set_index("no_island", inplace=True)
    width = grid_df.loc[1,'grid_width']
    height = grid_df.loc[1,'grid_height']
    n_islands = grid_df.last_valid_index()
    return grid_df, width, height, n_islands

def main() :
    print(read_grid_as_df(sys.argv[1]))

if __name__ == "__main__" : main()