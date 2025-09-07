#!/usr/bin/env python3

import explore

def main():
    e = explore.Explorer.for_problem('primus')
    res = e.explore_all_linear()
    explore.pp(res)
    e.write_example('inoutpair', **res)

if __name__ == '__main__':
    main()
