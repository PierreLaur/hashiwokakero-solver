"""A basic Hashiwokakero solver that takes a .has file as input and outputs a solution
use --a to find all solutions
"""
from ortools.sat.python import cp_model
import parse_has
import argparse
import os
from tqdm import tqdm


def solution_to_string(h_grid, solver, x_vars):
    """Returns a string representation of the grid solution"""

    # this could be more efficient - called a lot with --write option

    def replace_character(sol, i, j, char):
        """Inline helper to add an island or bridge in the solution"""
        sol[i] = sol[i][:j] + char + sol[i][j + 1 :]

    # empty grid with spaces
    empty_grid = [
        "   " * int(h_grid.width) + "\n" for j in range(2 * int(h_grid.height))
    ]

    # add islands
    for (i, j), d in zip(h_grid.island_coordinates, h_grid.digits):
        replace_character(empty_grid, 2 * i, 3 * j + 1, str(d))

    sol = ["%s" % line for line in empty_grid]

    # add bridges
    for bridge in x_vars.keys():
        if solver.Value(x_vars[bridge]) > 0:

            n_bridges = solver.Value(x_vars[bridge])
            coords_between, is_horizontal = coordinates_between(
                h_grid, bridge[0], bridge[1]
            )

            if not is_horizontal:
                replace_character(
                    sol,
                    2 * h_grid.island_coordinates[bridge[0]][0] + 1,
                    1 + 3 * h_grid.island_coordinates[bridge[0]][1],
                    "|" if n_bridges == 1 else "‖",
                )
                replace_character(
                    sol,
                    2 * h_grid.island_coordinates[bridge[1]][0] - 1,
                    1 + 3 * h_grid.island_coordinates[bridge[1]][1],
                    "|" if n_bridges == 1 else "‖",
                )
            else:
                replace_character(
                    sol,
                    2 * h_grid.island_coordinates[bridge[0]][0],
                    1 + 3 * h_grid.island_coordinates[bridge[0]][1] + 1,
                    "-" if n_bridges == 1 else "=",
                )
                replace_character(
                    sol,
                    2 * h_grid.island_coordinates[bridge[1]][0],
                    1 + 3 * h_grid.island_coordinates[bridge[1]][1] - 1,
                    "-" if n_bridges == 1 else "=",
                )

            for coords in coords_between:
                if not is_horizontal:
                    replace_character(
                        sol,
                        2 * coords[0],
                        1 + 3 * coords[1],
                        "|" if n_bridges == 1 else "‖",
                    )
                    if coords[0] > 0:
                        replace_character(
                            sol,
                            2 * coords[0] - 1,
                            1 + 3 * coords[1],
                            "|" if n_bridges == 1 else "‖",
                        )
                    if coords[0] < int(h_grid.width):
                        replace_character(
                            sol,
                            2 * coords[0] + 1,
                            1 + 3 * coords[1],
                            "|" if n_bridges == 1 else "‖",
                        )
                else:
                    if sol[2 * coords[0]][1 + 3 * coords[1]] in list(
                        map(str, list(range(1, 9)))
                    ):
                        print("Erasing island !")
                        print(bridge, coords)
                    replace_character(
                        sol,
                        2 * coords[0],
                        1 + 3 * coords[1],
                        "-" if n_bridges == 1 else "=",
                    )
                    if coords[1] > 0:
                        replace_character(
                            sol,
                            2 * coords[0],
                            1 + 3 * coords[1] - 1,
                            "-" if n_bridges == 1 else "=",
                        )
                    if coords[1] < int(h_grid.height):
                        replace_character(
                            sol,
                            2 * coords[0],
                            1 + 3 * coords[1] + 1,
                            "-" if n_bridges == 1 else "=",
                        )

    return "".join(sol)


def adjacent_islands(h_grid, island_index):
    """Returns the indexes of the islands that are adjacent to the input island"""

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
    for neighbour_index in range(island_index + 1, h_grid.n_islands):
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
    """
    Returns the list of coordinates a bridge between i and j would cross over
    Also returns 0 if the bridge is horizontal or 1 if it is vertical
    """
    # if the bridge is horizontal
    coordinates = []
    is_horizontal = False
    if h_grid.island_coordinates[i][0] == h_grid.island_coordinates[j][0]:
        x = h_grid.island_coordinates[i][0]
        coordinates = [
            (x, y)
            for y in range(
                h_grid.island_coordinates[i][1] + 1, h_grid.island_coordinates[j][1]
            )
        ]
        is_horizontal = True
    elif h_grid.island_coordinates[i][1] == h_grid.island_coordinates[j][1]:
        y = h_grid.island_coordinates[i][1]
        coordinates = [
            (x, y)
            for x in range(
                h_grid.island_coordinates[i][0] + 1, h_grid.island_coordinates[j][0]
            )
        ]
    return coordinates, is_horizontal


def intersect(h_grid, ai, aj, bi, bj):
    """Returns true if bridge a and bridge b intersect"""
    coords_under_a, bridge_a_horizontal = coordinates_between(h_grid, ai, aj)
    coords_under_b, bridge_b_horizontal = coordinates_between(h_grid, bi, bj)

    # if one bridge is vertical and the other horizontal
    if bridge_a_horizontal != bridge_b_horizontal:
        intersection = list(set(coords_under_a).intersection(coords_under_b))
        return bool(intersection)
    else:
        return False


def find_subtour(h_grid, solver, y_vars):
    """Returns a set of islands that form a subtour in a given solution,
    or None if there is no subtour"""

    # This could be more efficient

    # build a dict to determine where we can go from each island
    bridges = {island: [] for island in range(h_grid.n_islands)}
    for bridge, var in y_vars.items():
        if solver.Value(var):
            bridges[bridge[0]].append(bridge[1])
            bridges[bridge[1]].append(bridge[0])

    subtour_islands = {0}

    def scan(island):
        """Scans the bridge map recursively"""
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
        return None


def add_subtour_elimination(model, subtour_islands, y_vars):
    """Adds a subtour elimination constraint"""
    exiting_bridges = []
    for (from_island, to_island), y in y_vars.items():
        if (from_island in subtour_islands) != (to_island in subtour_islands):
            exiting_bridges.append(y)
    model.Add(sum(exiting_bridges) >= 1)


def write_solution(grid_name: str, solution: str):
    """Writes the solution to a file"""
    if not os.path.exists("solutions"):
        os.mkdir("solutions")
    file = os.path.join("solutions", grid_name)
    with open(file, "a+") as f:
        f.write(solution + "\n\n")


def solve_grid(h_grid, relaxed_model, x_vars, y_vars, write=False):
    """Finds a valid solution by solving the model and adding subtour elimination constraints when necessary"""

    model = relaxed_model
    subtours_eliminated_progressbar = tqdm(
        bar_format="Subtours eliminated : {n}", leave=False
    )
    while True:

        # Solve once
        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print("No solution found.")
            return solver, status

        # Find and eliminate a subtour in the solution
        subtour = find_subtour(h_grid, solver, y_vars)
        if subtour:
            add_subtour_elimination(model, subtour, y_vars)
            subtours_eliminated_progressbar.update()
        else:
            subtours_eliminated_progressbar.close()
            print(solution_to_string(h_grid, solver, x_vars), end="")
            print(
                f"Successfully solved the grid in {round(solver.UserTime(),3)} seconds"
            )
            if write:
                write_solution(h_grid.name, solution_to_string(h_grid, solver, x_vars))
                print(f'Wrote solution to {os.path.join("solutions",h_grid.name)}')
            return solver, status


def find_all_solutions(h_grid, relaxed_model, x_vars, y_vars, write=False):
    """Finds all solutions to the grid and outputs the number of solutions"""

    class SolutionCallback(cp_model.CpSolverSolutionCallback):
        """Called each time a solution is found. Counts the number of valid solutions found,
        checks for subtours
        and writes the results to a file if necessary
        """

        def __init__(
            self,
            model: cp_model.CpModel,
            h_grid,
            x_vars,
            y_vars,
            n_solutions_progressbar: tqdm,
            write: bool = False,
        ):
            self.model = model
            self.h_grid = h_grid
            self.x_vars = x_vars
            self.y_vars = y_vars

            self.solutions_all_valid = True
            self.n_valid_solutions = 0
            self.n_solutions_progressbar = n_solutions_progressbar
            self.write = write
            super().__init__()

        def OnSolutionCallback(self):
            """Called everytime a solution is found during search"""
            subtour = find_subtour(h_grid, self, y_vars)
            if subtour:
                self.solutions_all_valid = False
                add_subtour_elimination(self.model, subtour, y_vars)
                self.StopSearch()
            else:
                if self.n_valid_solutions == self.n_solutions_progressbar.n:
                    self.n_solutions_progressbar.update()
                self.n_valid_solutions += 1
                if self.n_valid_solutions == 1024:
                    self.n_solutions_progressbar.bar_format = "Minimum number of valid solutions : {n}          Press Ctrl+C to stop searching"
                if self.write:
                    write_solution(
                        self.h_grid.name,
                        solution_to_string(self.h_grid, self, self.x_vars),
                    )

    model = relaxed_model
    solved = False
    subtours_eliminated_progressbar = tqdm(
        bar_format="Subtours eliminated : {n}", leave=False
    )
    n_valid_solutions_progressbar = tqdm(
        bar_format="Minimum number of valid solutions : {n}", leave=False
    )
    while not solved:
        # print("Solving")

        solver = cp_model.CpSolver()
        solver.parameters.enumerate_all_solutions = True
        solution_callback = SolutionCallback(
            model, h_grid, x_vars, y_vars, n_valid_solutions_progressbar, write
        )
        status = solver.Solve(model, solution_callback=solution_callback)

        if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
            print("No solution found.")
            return solver, status

        if solution_callback.solutions_all_valid:
            solved = True
        else:
            subtours_eliminated_progressbar.update()
    subtours_eliminated_progressbar.close()
    n_valid_solutions_progressbar.close()

    print(
        f"\n{solution_callback.n_valid_solutions} valid solutions found. Last solution :"
    )
    print(solution_to_string(h_grid, solver, x_vars), end="")
    if write:
        print(f'Wrote solutions to {os.path.join("solutions",h_grid.name)}')

    return solver, status


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("has_file")
    parser.add_argument(
        "--a", default=False, action="store_true", help="Find all solutions"
    )
    parser.add_argument(
        "--write", default=False, action="store_true", help="Write solutions to a file"
    )
    args = parser.parse_args()
    
    h_grid = parse_has.read_has_file(args.has_file)
    if args.write:
        file = os.path.join("solutions", h_grid.name)
        if os.path.exists(file):
            ok = input(f"File {file} already exists ! Overwrite ? (y/n)")
            if ok not in ["y", "Y"]:
                print("Aborting")
                exit()
            else:
                os.remove(file)
        print(f'Warning : writing all solutions to a file may take a lot of disk space in {os.path.join(os.getcwd(),"solutions")} for big instances')

    model = cp_model.CpModel()
    if not model:
        return

    # declaring the variables
    x_vars = {}
    y_vars = {}

    for i in range(h_grid.n_islands):
        for j in range(i + 1, h_grid.n_islands):
            if j in adjacent_islands(h_grid, i):
                x_vars[(i, j)] = model.NewIntVar(0, 2, "x_" + str(i) + "_" + str(j))
                y_vars[(i, j)] = model.NewBoolVar("y_" + str(i) + "_" + str(j))

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
        model.Add(x <= 2 * y)

    # If two bridges intersect, one of them can be built at most
    for i, a in enumerate(y_vars):
        for b in list(y_vars.keys())[i + 1 :]:
            if intersect(h_grid, a[0], a[1], b[0], b[1]):
                model.Add(y_vars[a] + y_vars[b] <= 1)

    # Weak connectivity constraint
    model.Add(sum(y_vars.values()) >= h_grid.n_islands - 1)

    if args.a:
        solver, status = find_all_solutions(h_grid, model, x_vars, y_vars, args.write)
    else:
        solver, status = solve_grid(h_grid, model, x_vars, y_vars, args.write)


if __name__ == "__main__":
    main()
