import requests
import json

grid = json.load(open('puzzles/probabilistic/toy_grid_probs.json', 'r'))
res = requests.post('http://localhost:5000/solve', json=grid)

if res.ok:
    print(res.text)