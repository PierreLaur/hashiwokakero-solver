# Only one solution
# in sudoku : solve once, find another solution, if there is 2 then nogood() and repeat

# the bridges must begin and end on distinct islands
# they must not cross bridges or islands
# they may only run horizontally or vertically
# at most 2 bridges may connect any island pair
# the number of bridges connected to each island must be equal to the number inside the circle
# each island must be reachable from any other island

from ortools.sat.python import cp_model
# from ortools.constraint_solver import routing_enums_pb2
# from ortools.constraint_solver import pywrapcp

import parse_has
import sys

'''
Returns the list of coordinates a bridge between i and j would cross over
Also returns 0 if the bridge is horizontal or 1 if it is vertical
'''
def coordinates_between(h_grid,i,j) :
    # if the bridge is horizontal
    coordinates = []
    is_horizontal = False
    if h_grid.island_coordinates[i][0] == h_grid.island_coordinates[j][0] :
        x = h_grid.island_coordinates[i][0]
        coordinates = [(x,y) for y in range(h_grid.island_coordinates[i][1]+1, h_grid.island_coordinates[j][1])]
        is_horizontal = True
    elif h_grid.island_coordinates[i][1] == h_grid.island_coordinates[j][1]: 
        y = h_grid.island_coordinates[i][1]
        coordinates = [(x,y) for x in range(h_grid.island_coordinates[i][0]+1, h_grid.island_coordinates[j][0])]
    return coordinates, is_horizontal

'''
Returns true if bridge a and bridge b intersect
'''
def intersect(h_grid,ai,aj,bi,bj) :
    coords_under_a, bridge_a_horizontal = coordinates_between(h_grid,ai,aj)
    coords_under_b, bridge_b_horizontal = coordinates_between(h_grid,bi,bj) 

    # if one bridge is vertical and the other horizontal
    if bridge_a_horizontal != bridge_b_horizontal :
        intersection = list(set(coords_under_a).intersection(coords_under_b))
        return bool(intersection)
    else : return False

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

    # The sum of bridges connected to an island must be equal to the number of digits 
    for k in range(h_grid.n_islands) :
        vars_to_sum = []
        for i, (a,b) in enumerate(h_grid.island_coordinates[:k]) :
            if h_grid.island_coordinates[k][0] == a or h_grid.island_coordinates[k][1] == b :
                vars_to_sum.append(x_vars[(i,k)])
        for j,(a,b) in enumerate(h_grid.island_coordinates[k+1:]) :
            if h_grid.island_coordinates[k][0] == a or h_grid.island_coordinates[k][1] == b :            
                vars_to_sum.append(x_vars[(k,j+k+1)])
        model.Add(sum(vars_to_sum) == h_grid.digits[k])

    # If there is a bridge between i and j, x must be >0 and <=2
    # If there is no bridge between i and j, x must be =0
    for (x,y) in zip(x_vars.values(), y_vars.values()) :
        model.Add(y <= x)
        model.Add(x <= 2*y)

    # If two bridges intersect, one of them can be built at most
    for i,a in enumerate(y_vars) :
        for b in list(y_vars.keys())[i+1:] :
            if intersect(h_grid, a[0], a[1], b[0], b[1]) :
                model.Add(y_vars[a] + y_vars[b] <= 1)



    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # print the result
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for i in x_vars.keys() :
            if solver.Value(x_vars[i]) > 0 :
                print(f"{solver.Value(x_vars[i])} bridges from island {i[0]} to island {i[1]}")

    else:
        print('No solution found.')

if __name__ == '__main__':
    main()