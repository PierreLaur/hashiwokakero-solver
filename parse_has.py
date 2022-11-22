import sys

count = 0
file = sys.argv[1]
grid = []
with open(file) as f :
    width, height, n_islands = f.readline().split()
    for line in f :
        grid.append(list(map(lambda x : int(x), line.strip().split())))

print(f'Width : {width} \nHeight : {height} \nNumber of islands : {n_islands} \n\n The grid : ')
print(grid)