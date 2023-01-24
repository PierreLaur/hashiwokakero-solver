"""An example of POST request that could be sent to the probabilistic solver's Flask API
"""
import requests
import json

dir = "puzzles/probabilistic/100"
grid = json.load(open(dir + "/" + "Hs_16_100_25_00_001.json", "r"))
res = requests.post("http://localhost:5000/solve", json=grid)

if res.ok:
    print(res.text)
