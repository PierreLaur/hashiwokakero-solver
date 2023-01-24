import json
import numpy as np
import os


def generate_probs_grid(has_grid):
    json_grid = {}
    json_grid["islands"] = []
    with open(has_grid, "r") as f:
        lines = f.read().split("\n")
        json_grid["width"] = lines[0].strip().split()[0]
        json_grid["height"] = lines[0].strip().split()[1]
        for row, line in enumerate(lines[1:]):
            digits = line.strip().split()
            for col, d in enumerate(digits):
                if d != "0":
                    digits_probs = np.random.randint(0, 10, 8)
                    digits_probs[int(d) - 1] += 5
                    digits_probs = list(digits_probs / np.linalg.norm(digits_probs))
                    json_grid["islands"].append(
                        {"row": row, "col": col, "digits_probabilities": digits_probs}
                    )
    return json_grid


def copy_all_has_grids():
    """Creates json grids from the big .has dataset
    These grids are incorrect, they allow multiple solutions (our probabilistic solver will not work)
    """
    
    write_path = os.path.join(os.getcwd(),'puzzles','probabilistic')
    read_path = os.path.join(os.getcwd(),'puzzles','basic')
    ok = input(f"Write probabilistic puzzles to {write_path} (about 75 MB total) (y/n)")
    if ok not in ["y", "Y"] :
        print("Aborted")
        exit()
        
    for size in ["100", "200", "300", "400"]:
        write_path_size = os.path.join(write_path, size)
        read_path_size = os.path.join(read_path, size)
        if not os.path.exists(write_path_size):
            os.mkdir(write_path_size)
        files_to_copy = os.listdir(read_path_size)
        for file_to_copy in files_to_copy:

            json_grid = generate_probs_grid(
                os.path.join(read_path_size, file_to_copy)
            )
            new_file = (
                os.path.join(write_path_size,
                    os.path.splitext(file_to_copy)[0]
                    + ".json")
            )
            with open(new_file, "w") as f:
                json.dump(json_grid, f)
                print("Writing json grid to " + new_file)


def main():
    copy_all_has_grids()
    # generate_probs_grid(sys.argv[1])


if __name__ == "__main__":
    main()
