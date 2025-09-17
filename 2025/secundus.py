#!/usr/bin/env python3

from explorer import Explorer
from bifurcation_solver import BifurcationSolver

from secret import ID


def main():
    explorer = Explorer("http://localhost", ID, "secundus")
    explorer.start()

    solver = BifurcationSolver(explorer)
    solver.solve()

if __name__ == '__main__':
    main()
