#!/usr/bin/env python3

from collections import deque
from pathlib import Path
from pprint import pprint as pp

import typer
import ptpython

import data

def main():
    typer.run(load_and_solve)

def load_and_solve(json_fpath: Path):
    obj = data.InOutPairs.load(json_fpath)
    data.show(obj)

    solve_state = data.LabelSets.for_rooms(obj.num_rooms)
    data.show(solve_state)

    # For now, things to explore are a combination of (index to input/output:results, index of character in the string
    num_indices = len(obj.input)
    to_explore = deque((i, 0) for i in range(num_indices))


    count = 0 
    max_count = 100
    while to_explore:
        count += 1
        if count > max_count:
            break

        input_i, str_i = to_explore.popleft()
        input_ = obj.input[input_i]
        if str_i < len(input_):
            to_explore.append((input_i, str_i+1))
        result = obj.output.results[input_i]
        door_list = input_[:str_i]
        cur_room = result[str_i]
        outgoing_door = data.Door(input_[str_i]).value
        outgoing_room = data.RoomLabel(result[str_i+1])
        label_classes = solve_state.label_map[cur_room]
        print(f'{input_i}:{str_i} -> {door_list} {cur_room} D{outgoing_door}:L{outgoing_room}')

        if door_list in label_classes.paths_to_labelmaps:
            labelmap = label_classes.paths_to_labelmaps[door_list].paths_to_labels
            if outgoing_door not in labelmap:
                labelmap[outgoing_door] = outgoing_room

            else: # outgoing_door already exists in map
                existing_room = labelmap[outgoing_door]
                if existing_room == outgoing_room:
                    # we don't need to do anything here, at the moment, may need to add additional things to explore in future
                    pass
                else:
                    # in this case, we would have the same path having two different rooms from the same door, this should
                    # be impossible
                    raise RuntimeError('how did we get here?')
        else:
            new_paths_to_labels = {outgoing_door: outgoing_room}
            labelmap = data.LabelMap(paths_to_labels=new_paths_to_labels, first_path=door_list)
            label_classes.paths_to_labelmaps[door_list] = labelmap
            label_classes.min_classes = max(label_classes.min_classes, 1)

    data.show(solve_state)

    ptpython.embed(globals(), locals(), configure=no_quit_confirm)

def no_quit_confirm(repl):
    repl.confirm_exit = False
        

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
# From a label, we have the following:
# { door_list: label }
# Once we have sum(min_classes(label) for all labels) == num_rooms, then we are done
#
# We need to handle a bucket of paths that we don't know which class they are in, because even once we know how many
# classes there are, and have a unique reprentative of each, we don't know necessarily WHICH class each existing path goes to






if __name__ == '__main__':
    main()

