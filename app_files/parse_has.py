import sys
import json


class HashiGrid:
    def __init__(self, width, height, n_islands) -> None:
        self.width = width
        self.height = height

        self.n_islands = n_islands

        self.island_coordinates = []
        self.digits = []

    def fill_grid(self, grid):
        for i, line in enumerate(grid):
            for j, square in enumerate(line):
                if square != 0:
                    self.island_coordinates.append(
                        (i, j)
                    )
                    self.digits.append(square)

    def print_grid(self):
        for coords, d in zip(self.island_coordinates, self.digits):
            print(f'Island {coords}    with n_bridges = {d}')


def read_has_file(file):
    file = sys.argv[1]
    grid = []
    with open(file) as f:
        width, height, n_islands = f.readline().split()
        for line in f:
            grid.append(list(map(lambda x: int(x), line.strip().split())))

    h_grid = HashiGrid(width, height, int(n_islands))
    h_grid.fill_grid(grid)

    return h_grid


class ProbabilisticHashiGrid:
    def __init__(self, width, height, n_islands, precision) -> None:
        self.width = width
        self.height = height
        self.n_islands = n_islands
        self.precision = precision

        self.island_coordinates = []

        self.probs = {}
        self.digits = []

    def fill_grid(self, islands, model):
        for l in range(self.n_islands):
            island_coords = (islands[l]['row'], islands[l]['col'])
            self.island_coordinates.append(island_coords)
            self.probs[l] = [0]+[round((10**self.precision)*i)
                                 for i in islands[l]['digits_probabilities']]
            self.digits.append(model.NewIntVar(1, 8, f'd_{l}'))

    # def eliminate_combination

    def print_grid(self):
        for coords, d in zip(self.island_coordinates, self.digits):
            print(f'Island {coords}    with n_bridges = {d}')


def read_json_grid(grid_json):

    width = grid_json['width']
    height = grid_json['height']

    islands = grid_json['islands']
    n_islands = len(islands)
    return islands, width, height, n_islands


def main():
    with open(sys.argv[1], 'r') as f:
        grid_json = json.load(f)
    islands, width, height, n_islands = read_json_grid(grid_json)
    print(n_islands, width, height)
    for island in islands:
        print(island)


if __name__ == "__main__":
    main()
