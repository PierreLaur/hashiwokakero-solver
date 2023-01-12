from ortools.sat.python import cp_model
import time
import parse_has
import sys
import os
import json
import argparse

PRECISION_N_DIGITS = 5


def print_solution(h_grid, solver, x_vars, write_solutions=True):
    """
    Inline helper to add an island or bridge in the solution
    """
    def replace_character(sol, i, j, char):
        sol[i] = sol[i][:j] + char + sol[i][j+1:]

    # empty grid with spaces
    empty_grid = ["   " * int(h_grid.width)+"\n"
                  for j in range(2*int(h_grid.height))]

    # add islands
    for (i, j), d in zip(h_grid.island_coordinates, h_grid.digits):
        replace_character(empty_grid, 2*i, 3*j+1, str(solver.Value(d)))

    sol = ['%s' % line for line in empty_grid]

    # add bridges
    for bridge in x_vars.keys():
        if solver.Value(x_vars[bridge]) > 0:

            n_bridges = solver.Value(x_vars[bridge])
            coords_between, is_horizontal = coordinates_between(
                h_grid, bridge[0], bridge[1])

            if not is_horizontal:
                replace_character(sol, 2*h_grid.island_coordinates[bridge[0]][0]+1,
                                  1 + 3 * h_grid.island_coordinates[bridge[0]][1], "|" if n_bridges == 1 else "‖")
                replace_character(sol, 2*h_grid.island_coordinates[bridge[1]][0]-1,
                                  1 + 3 * h_grid.island_coordinates[bridge[1]][1], "|" if n_bridges == 1 else "‖")
            else:
                replace_character(
                    sol, 2*h_grid.island_coordinates[bridge[0]][0], 1+3*h_grid.island_coordinates[bridge[0]][1]+1, "-" if n_bridges == 1 else "=")
                replace_character(
                    sol, 2*h_grid.island_coordinates[bridge[1]][0], 1+3*h_grid.island_coordinates[bridge[1]][1]-1, "-" if n_bridges == 1 else "=")

            for coords in coords_between:
                if not is_horizontal:
                    replace_character(
                        sol, 2*coords[0], 1+3*coords[1], "|" if n_bridges == 1 else "‖")
                    if coords[0] > 0:
                        replace_character(
                            sol, 2*coords[0]-1, 1+3*coords[1], "|" if n_bridges == 1 else "‖")
                    if coords[0] < int(h_grid.width):
                        replace_character(
                            sol, 2*coords[0]+1, 1+3*coords[1], "|" if n_bridges == 1 else "‖")
                else:
                    if sol[2*coords[0]][1+3*coords[1]] in list(map(str, list(range(1, 9)))):
                        print('Erasing island !')
                        print(bridge, coords)
                    replace_character(
                        sol, 2*coords[0], 1+3*coords[1], "-" if n_bridges == 1 else "=")
                    if coords[1] > 0:
                        replace_character(
                            sol, 2*coords[0], 1+3*coords[1]-1, "-" if n_bridges == 1 else "=")
                    if coords[1] < int(h_grid.height):
                        replace_character(
                            sol, 2*coords[0], 1+3*coords[1]+1, "-" if n_bridges == 1 else "=")

    if write_solutions:
        # print to a file
        if not os.path.exists('solved_grids'):
            os.mkdir('solved_grids')
        i = 0
        while os.path.exists("solved_grids/probabilistic_%s" % i):
            i += 1
        output_file = open("solved_grids/probabilistic_%s" % i, "w")
        output_file.writelines(sol)

    return ''.join(empty_grid), ''.join(sol)


def adjacent_islands(h_grid, island_index):
    """Returns the indexes of the islands that are adjacent to the input island
    """

    adjacent_islands = []
    island_xcoord, island_ycoord = h_grid.island_coordinates[island_index]

    top_neighbour_found = False
    left_neighbour_found = False
    for neighbour_index in reversed(range(island_index)):
        neighbour_xcoord, neighbour_ycoord = h_grid.island_coordinates[neighbour_index]
        if not left_neighbour_found and island_xcoord == neighbour_xcoord:
            left_neighbour_found = True
            adjacent_islands.append(neighbour_index)
        if not top_neighbour_found and island_ycoord == neighbour_ycoord:
            top_neighbour_found = True
            adjacent_islands.append(neighbour_index)

        if left_neighbour_found and top_neighbour_found:
            break

    bottom_neighbour_found = False
    right_neighbour_found = False
    for neighbour_index in range(island_index+1, h_grid.n_islands):
        neighbour_xcoord, neighbour_ycoord = h_grid.island_coordinates[neighbour_index]
        if not right_neighbour_found and island_xcoord == neighbour_xcoord:
            right_neighbour_found = True
            adjacent_islands.append(neighbour_index)
        if not bottom_neighbour_found and island_ycoord == neighbour_ycoord:
            bottom_neighbour_found = True
            adjacent_islands.append(neighbour_index)

        if right_neighbour_found and bottom_neighbour_found:
            break

    return adjacent_islands


def coordinates_between(h_grid, i, j):
    '''
    Returns the list of coordinates a bridge between i and j would cross over
    Also returns 0 if the bridge is horizontal or 1 if it is vertical
    '''
    # if the bridge is horizontal
    coordinates = []
    is_horizontal = False
    if h_grid.island_coordinates[i][0] == h_grid.island_coordinates[j][0]:
        x = h_grid.island_coordinates[i][0]
        coordinates = [(x, y) for y in range(
            h_grid.island_coordinates[i][1]+1, h_grid.island_coordinates[j][1])]
        is_horizontal = True
    elif h_grid.island_coordinates[i][1] == h_grid.island_coordinates[j][1]:
        y = h_grid.island_coordinates[i][1]
        coordinates = [(x, y) for x in range(
            h_grid.island_coordinates[i][0]+1, h_grid.island_coordinates[j][0])]
    return coordinates, is_horizontal


def intersect(h_grid, ai, aj, bi, bj):
    """Returns true if bridge a and bridge b intersect
    """
    coords_under_a, bridge_a_horizontal = coordinates_between(h_grid, ai, aj)
    coords_under_b, bridge_b_horizontal = coordinates_between(h_grid, bi, bj)

    # if one bridge is vertical and the other horizontal
    if bridge_a_horizontal != bridge_b_horizontal:
        intersection = list(set(coords_under_a).intersection(coords_under_b))
        return bool(intersection)
    else:
        return False


def find_subtour(h_grid, solver, y_vars):

    # build a dict to determine where we can go from each island
    bridges = {island: [] for island in range(h_grid.n_islands)}
    for bridge, var in y_vars.items():
        if solver.Value(var):
            bridges[bridge[0]].append(bridge[1])
            bridges[bridge[1]].append(bridge[0])

    subtour_islands = {0}

    def scan(island):
        '''Scans the bridge map recursively
        '''
        while bridges[island]:
            successor = bridges[island][0]
            subtour_islands.add(successor)
            bridges[island].remove(successor)
            bridges[successor].remove(island)
            scan(successor)

    scan(0)
    if len(subtour_islands) != h_grid.n_islands:
        return subtour_islands
    else:
        return []


def add_subtour_elimination(model, subtour_islands, y_vars):
    exiting_bridges = []
    for (from_island, to_island), y in y_vars.items():
        if (from_island in subtour_islands) != (to_island in subtour_islands):
            exiting_bridges.append(y)
    model.Add(sum(exiting_bridges) >= 1)


class HashiSolutionPrinter(cp_model.ObjectiveSolutionPrinter):
    """ may be used to print intermediate solutions """

    def __init__(self, h_grid, x_variables, y_variables):
        self.x_variables = x_variables
        self.y_variables = y_variables
        self.h_grid = h_grid
        super().__init__()

    def OnSolutionCallback(self):
        print_solution(self.h_grid, self, self.x_variables)
        if self.solution_count() > 0:
            self.StopSearch()
        return super().OnSolutionCallback()
        # return


def branch_and_cut(h_grid, relaxed_model, y_vars, log=False):
    """Applies the Branch And Cut algorithm, starting from the relaxed model (without subtour elimination)
    """

    model = relaxed_model
    while True:
        # try without remaking a solver
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            if log:
                print("No solution found")
            return solver, status

        if log:
            print("Potential solution, checking subtours")
        subtour = find_subtour(h_grid, solver, y_vars)
        if subtour:
            if log:
                print("    Eliminating subtour")
            add_subtour_elimination(model, subtour, y_vars)
            continue
        else:
            return solver, status


def solve_grid(json_grid, write_solutions=True, log=False, solution_is_unique=False):

    start_time = time.time()

    if PRECISION_N_DIGITS <= 0 or PRECISION_N_DIGITS > 17:
        print("Precision (number of digits) must be >0 and <=17")
        return

    islands, width, height, n_islands = parse_has.read_json_grid(json_grid)

    model = cp_model.CpModel()
    if not model:
        return

    h_grid = parse_has.ProbabilisticHashiGrid(
        width, height, n_islands, PRECISION_N_DIGITS)
    h_grid.fill_grid(islands, model)

    # declaring the variables
    x_vars = {}
    y_vars = {}

    for i in range(h_grid.n_islands):
        for j in range(i+1, h_grid.n_islands):
            if j in adjacent_islands(h_grid, i):
                x_vars[(i, j)] = model.NewIntVar(0, 2, 'x_'+str(i)+"_"+str(j))
                y_vars[(i, j)] = model.NewBoolVar('y_'+str(i)+"_"+str(j))

    # First constraint : The sum of bridges connected to an island must be equal to the number of digits
    for i in range(h_grid.n_islands):
        adjacent_xvars = []
        for j in adjacent_islands(h_grid, i):
            adjacent_xvars.append(x_vars[((i, j) if i < j else (j, i))])

        model.Add(sum(adjacent_xvars) == h_grid.digits[i])

    # If there is a bridge between i and j, x must be >0 and <=2
    # If there is no bridge between i and j, x must be =0
    for (x, y) in zip(x_vars.values(), y_vars.values()):
        model.Add(y <= x)
        model.Add(x <= 2*y)

    # If two bridges intersect, one of them can be built at most
    for i, a in enumerate(y_vars):
        for b in list(y_vars.keys())[i+1:]:
            if intersect(h_grid, a[0], a[1], b[0], b[1]):
                model.Add(y_vars[a] + y_vars[b] <= 1)

    # Weak connectivity constraint
    model.Add(sum(y_vars.values()) >= h_grid.n_islands-1)

    # Probabilities of the digits (the objective to maximize)
    digits_probs = {}
    probs_upper_bound = 0
    for i in range(n_islands):
        digits_probs[i] = model.NewIntVar(0, 10**PRECISION_N_DIGITS, f'dp_{i}')
        model.AddElement(h_grid.digits[i], h_grid.probs[i], digits_probs[i])
        probs_upper_bound += max(h_grid.probs[i])

    # Maximize the probabilities of the digits
    model.Maximize(sum(digits_probs.values()))

    solved = False
    while not solved:

        # solve with branch and cut to eliminate subtours

        solver, status = branch_and_cut(h_grid, model, y_vars, log=log)
        confidence = 1
        for dp in digits_probs.values() :
            confidence *= solver.Value(dp) / 10**PRECISION_N_DIGITS

        # If the solution isn't unique, we found a solution
        #  (there is at least one solution with this digit combination)
        if not solution_is_unique:
            break

        # If no solution, disallow this digit assignment
        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            model.AddForbiddenAssignments(
                h_grid.digits, [solver.Value(d) for d in h_grid.digits])
            continue

        else:
            if log:
                print("    No subtours, checking if solution is unique")
                print(f"    Confidence : {confidence}")

            # Check if there is multiple solutions with the previously found digit assignment
            aux_model = cp_model.CpModel()
            aux_model.CopyFrom(model)

            aux_model.AddAllowedAssignments(
                h_grid.digits, [tuple([solver.Value(d) for d in h_grid.digits])])
            aux_model.ClearObjective()

            aux_solver = cp_model.CpSolver()
            aux_solver.parameters.enumerate_all_solutions = True
            solution_printer = HashiSolutionPrinter(h_grid, x_vars, y_vars)
            status = aux_solver.Solve(aux_model, solution_printer)

            # If multiple solutions exist, the digits were not correct, try again
            if solution_printer.solution_count() > 1:
                if log:
                    print("        Solution is not unique, retrying")

                model.AddForbiddenAssignments(
                    h_grid.digits, [tuple([solver.Value(d) for d in h_grid.digits])])

            else:
                if log:
                    print("        Solution is unique !")
                solved = True

    empty_grid, solved_grid = print_solution(
        h_grid, solver, x_vars, write_solutions)

    return "Solution : \n" + solved_grid +\
        f"Confidence : {confidence*100}%\n" +\
        f'Successfully solved the grid in {round(time.time()-start_time,3)} seconds'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("grid")
    parser.add_argument("--solution_is_unique", action="store_true")

    args = parser.parse_args()
    solution_is_unique = True if args.solution_is_unique else False

    with open(args.grid, 'r') as f:
        grid_json = json.load(f)

    result = solve_grid(grid_json, log=True,
                        solution_is_unique=solution_is_unique)
    print(result)


if __name__ == '__main__':
    main()
