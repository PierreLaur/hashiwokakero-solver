# Only one solution
# in sudoku : solve once, find another solution, if there is 2 then nogood() and repeat

# the bridges must begin and end on distinct islands
# they must not cross bridges or islands
# they may only run horizontally or vertically
# at most 2 bridges may connect any island pair
# the number of bridges connected to each island must be equal to the number inside the circle
# each island must be reachable from any other island

from ortools.sat.python import cp_model

def main() :
    model = cp_model.CpModel()
    if not model :
        return

    num_vals = 3
    x = model.NewIntVar(0, num_vals - 1, 'x')
    y = model.NewIntVar(0, num_vals - 1, 'y')
    z = model.NewIntVar(0, num_vals - 1, 'z')

    model.Add(x != y)


    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print('x = %i' % solver.Value(x))
        print('y = %i' % solver.Value(y))
        print('z = %i' % solver.Value(z))
    else:
        print('No solution found.')

if __name__ == '__main__':

    main()