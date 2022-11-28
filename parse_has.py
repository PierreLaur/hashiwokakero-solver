import sys
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
    count = 0
    file = sys.argv[1]
    grid = []
    with open(file) as f :
        width, height, n_islands = f.readline().split()
        for line in f :
            grid.append(list(map(lambda x : int(x), line.strip().split())))

    h_grid = HashiGrid(width, height, int(n_islands))
    h_grid.fill_grid(grid)
    
    return h_grid
