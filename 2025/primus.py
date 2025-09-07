#!/usr/bin/env python3

import explore

from secret import ID

def main():
    e = explore.Explorer.for_problem('primus', id_=ID)
    res = e.explore_all_linear()
    explore.pp(res)
    e.write_example('inoutpair', **res)

if __name__ == '__main__':
    main()
