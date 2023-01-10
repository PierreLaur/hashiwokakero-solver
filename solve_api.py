from flask import Flask, request
from probabilistic_solver import solve_grid
app = Flask(__name__)


@app.route('/solve', methods=["POST"])
def test():
    grid = request.get_json(silent=True)
    return solve_grid(grid)


if __name__ == '__main__':
    app.run()