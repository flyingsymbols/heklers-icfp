#!/usr/bin/env python3

from pathlib import Path
from pprint import pprint as pp

import typer

import data

def main():
    typer.run(load_and_solve)

def load_and_solve(json_fpath: Path):
    obj = data.InOutPairs.load(json_fpath)
    data.show(obj)

# Approach:
# we can uniquely identify paths, via a sequence rooted at the start room.
# These sequences can be viewed as (start_label, [(door, label)]).
# if we are willing to be a bit loose with notation, we can represent this even as a string, where every even index
# (starting with 0), is a room label, and every odd index (starting with 1), is a door index
#
# How do we differentiate rooms?:
# Whenever a label is different, we know that there are different rooms.
# However, even on primus, we have more rooms than labels. How do we differentiate these?
# Key insight: whenever we have the same outgoing door from the same label prefix, and a different labeled destination
# we can seperate the rooms into classes.
# We can keep doing this until the number of classes equals the number of rooms.
# For a given class, we can use a union-find type of datastructure in order to keep count of the possibilities
# For this datastructure, we will initialize it with min_classes = num_rooms and max_classes = num_rooms


if __name__ == '__main__':
    main()

