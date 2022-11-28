# Only one solution
# in sudoku : solve once, find another solution, if there is 2 then nogood() and repeat

# the bridges must begin and end on distinct islands
# they must not cross bridges or islands
# they may only run horizontally or vertically
# at most 2 bridges may connect any island pair
# the number of bridges connected to each island must be equal to the number inside the circle
# each island must be reachable from any other island

from ortools.sat.python import cp_model

import parse_has
import sys

def adjacent_vertices(coords, vertices) :
    adj = []
    for vertice in vertices :
        if vertice[0] == coords[0] or vertice[1] == coords[1] :
            adj.append((island[0],island[1]))
    return adj

def main() :

    h_grid = parse_has.read_has_file(sys.argv[1])

    model = cp_model.CpModel()
    if not model :
        return

    # declaring the variables
    x_vars = {}
    y_vars = {}

    for i in range(h_grid.n_islands) :
        for j in range(i+1, h_grid.n_islands) :
            x_vars[(i,j)] = model.NewIntVar(0,2,'x_'+str(i)+"_"+str(j))
            y_vars[(i,j)] = model.NewBoolVar('y_'+str(i)+"_"+str(j))

    # constraints
    for k in range(h_grid.n_islands) :
        vars_to_sum = []
        for i, (a,b) in enumerate(h_grid.island_coordinates[:k]) :
            if h_grid.island_coordinates[k][0] == a or h_grid.island_coordinates[k][1] == b :
                vars_to_sum.append(x_vars[(i,k)])
        for j,(a,b) in enumerate(h_grid.island_coordinates[k+1:]) :
            if h_grid.island_coordinates[k][0] == a or h_grid.island_coordinates[k][1] == b :            
                vars_to_sum.append(x_vars[(k,j+k+1)])
        model.Add(sum(vars_to_sum) == 1)
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # print the result
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for i in x_vars.keys() :
            if solver.Value(x_vars[i]) > 0 :
                print(f"{i} {solver.Value(x_vars[i])} bridges")

    else:
        print('No solution found.')

if __name__ == '__main__':
    main()