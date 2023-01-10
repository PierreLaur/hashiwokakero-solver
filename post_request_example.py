import requests
import json
import numpy as np
import os

dir = 'puzzles/probabilistic/100'
files = os.listdir(dir)
file = np.random.choice(files)

# grid = json.load(open(dir+'/'+file, 'r'))
grid = json.load(open(dir+'/'+'Hs_16_100_25_00_001.json', 'r'))
res = requests.post('http://localhost:5000/solve', json=grid)

if res.ok:
    print(res.text)
