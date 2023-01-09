import json
import numpy as np
import os


def generate_probs_grid(has_grid):
    json_grid = {}
    json_grid['islands'] = []
    with open(has_grid, 'r') as f:
        lines = f.read().split("\n")
        json_grid['width'] = lines[0].strip().split()[0]
        json_grid['height'] = lines[0].strip().split()[1]
        for row, line in enumerate(lines[1:]):
            digits = line.strip().split()
            for col, d in enumerate(digits):
                if d != '0':
                    digits_probs = np.random.randint(0, 10, 8)
                    digits_probs[int(d)-1] += 5
                    digits_probs = list(
                        digits_probs / np.linalg.norm(digits_probs))
                    json_grid['islands'].append(
                        {'row': row, 'col': col, 'digits_probabilities': digits_probs})
    return json_grid


def main():

    for size in ['100', '200', '300', '400']:
        files_to_copy = os.listdir('puzzles/basic/' + size)
        for file_to_copy in files_to_copy:

            json_grid = generate_probs_grid(
                'puzzles/basic/'+size+'/'+file_to_copy)
            new_file = 'puzzles/probabilistic/' + size + \
                '/' + os.path.splitext(file_to_copy)[0]+'.json'
            with open(new_file, 'w') as f:
                json.dump(json_grid, f)
                print('Writing json grid to ' + new_file)


if __name__ == '__main__':
    main()
