"""
Unit tests conftest
"""

import os
import sys
from copy import deepcopy
from random import shuffle
from types import SimpleNamespace

import pytest

from ..conftest import AEDIFICIUM_PATH

AEDIFICIUM_SERVER_PATH = os.path.join(AEDIFICIUM_PATH, "server")

sys.path.insert(0, AEDIFICIUM_SERVER_PATH)

from problem_session import MapField, ProblemSession # pylint: disable=wrong-import-position, wrong-import-order

EXAMPLE_PROBATIO = SimpleNamespace(
    door_index={
        (1, 1): (2, 5),
        (2, 5): (1, 1),
        (2, 3): (1, 2),
        (1, 2): (2, 3),
        (1, 0): (2, 1),
        (2, 1): (1, 0),
        (0, 5): (0, 1),
        (0, 1): (0, 5),
        (1, 3): (1, 3),
        (1, 5): (1, 5),
        (1, 4): (0, 4),
        (0, 4): (1, 4),
        (0, 0): (2, 4),
        (2, 4): (0, 0),
        (2, 0): (2, 2),
        (2, 2): (2, 0),
        (0, 2): (0, 3),
        (0, 3): (0, 2),
    },
    hintified=[
        ((0, 0), (1, 2, 3, 5)),
        ((0, 1), (4,)),
        ((0, 2), (0,)),
        ((1, 0), (4,)),
        ((1, 1), (3, 5)),
        ((1, 2), (0, 1, 2)),
        ((2, 0), (4,)),
        ((2, 1), (1, 3, 5)),
        ((2, 2), (0, 2)),
    ],
)

EXAMPLE_PRIMUS = SimpleNamespace(
    door_index={
        (5, 5): (3, 4),
        (3, 4): (5, 5),
        (0, 2): (5, 1),
        (5, 1): (0, 2),
        (2, 4): (0, 5),
        (0, 5): (2, 4),
        (4, 1): (5, 3),
        (5, 3): (4, 1),
        (3, 2): (3, 1),
        (3, 1): (3, 2),
        (4, 0): (3, 3),
        (3, 3): (4, 0),
        (1, 1): (2, 3),
        (2, 3): (1, 1),
        (4, 3): (5, 2),
        (5, 2): (4, 3),
        (4, 5): (0, 4),
        (0, 4): (4, 5),
        (1, 0): (4, 2),
        (4, 2): (1, 0),
        (0, 3): (1, 2),
        (1, 2): (0, 3),
        (2, 2): (3, 0),
        (3, 0): (2, 2),
        (1, 4): (5, 4),
        (5, 4): (1, 4),
        (0, 0): (2, 5),
        (2, 5): (0, 0),
        (2, 1): (3, 5),
        (3, 5): (2, 1),
        (0, 1): (0, 1),
        (1, 3): (2, 0),
        (2, 0): (1, 3),
        (1, 5): (1, 5),
        (4, 4): (5, 0),
        (5, 0): (4, 4),
    },
    hintified=[
        ((0, 0), (1,)),
        ((0, 0), (4,)),
        ((0, 0), (5,)),
        ((0, 1), (1, 3, 4)),
        ((0, 1), (2,)),
        ((0, 1), (2,)),
        ((0, 1), (3,)),
        ((0, 2), (0, 5)),
        ((0, 3), (0,)),
        ((1, 0), (0,)),
        ((1, 0), (0, 2, 3)),
        ((1, 0), (1,)),
        ((1, 0), (2,)),
        ((1, 1), (4,)),
        ((1, 1), (4,)),
        ((1, 1), (5,)),
        ((1, 2), (1, 3)),
        ((1, 3), (5,)),
        ((2, 0), (4, 5)),
        ((2, 1), (0, 3)),
        ((2, 3), (1, 2)),
        ((3, 0), (3,)),
        ((3, 1), (4,)),
        ((3, 2), (0, 5)),
        ((3, 3), (1, 2)),
    ],
)


@pytest.fixture(scope="function", params=[EXAMPLE_PROBATIO, EXAMPLE_PRIMUS])
def problem(request):
    """
    Parametrized fixture that produces the example problem instances
    """
    example = request.param
    problem_session = ProblemSession("probatio")
    problem_session.door_index = example.door_index
    problem_session.hintified = example.hintified
    return problem_session


def door_index_to_guess(door_index, number_of_rooms):
    """
    Build a guess MapField structure from a door_index
    """
    return MapField(
        **{
            "rooms": range(number_of_rooms),
            "startingRoom": 0,
            "connections": [
                {
                    "from": {
                        "room": from_room,
                        "door": from_door,
                    },
                    "to": {
                        "room": to_room,
                        "door": to_door,
                    },
                }
                for (from_room, from_door), (to_room, to_door) in door_index.items()
            ],
        }
    )


def shuffle_rooms(door_index, number_of_rooms):
    """
    Shuffles room numbers in such a way that the 2 bit "hint" remains constant returning a new door_index
    """
    if number_of_rooms <= 3:
        # room numbers are unique
        return door_index

    room_number_remap = {}
    for hint in range(3):
        # get all the rooms that match this hint
        hint_rooms = range(hint, number_of_rooms, 4)
        # shuffle them and create a from/to mapping
        new_rooms = deepcopy(hint_rooms)
        shuffle(new_rooms)
        for orig, new in zip(hint_rooms, new_rooms):
            room_number_remap[orig] = new

    return {
        (room_number_remap[from_room], from_door): (room_number_remap[to_room], to_door)
        for (from_room, from_door), (to_room, to_door) in door_index.items()
    }


def shuffle_all_door_mappings(door_index, number_of_rooms):
    """
    For good measure, just shuffle all the door mappings

    For example if room 1 doors 2, 3 get you to room 2, and room 2 doors 4, 5 get you to room 1,
    then it's equally valid to assume any pairs of doors link to each other:
    {(1, 2):(2, 4), (1, 3):(2, 5)} or {(1, 3):(2, 4), (1, 2):(2, 5)}
    """
    door_index = deepcopy(door_index)
    for room1 in range(number_of_rooms):
        for room2 in range(number_of_rooms):
            _shuffle_door_mappings(door_index, room1, room2)
    return door_index


def _shuffle_door_mappings(door_index, room1, room2):
    """
    Shuffle the door mappings for a pair of rooms, returning a new door_index
    """
    from_to_doors = list(
        filter(
            lambda from_to: from_to[0][0] == room1 and from_to[1][0] == room2,
            door_index.items(),
        )
    )
    if len(from_to_doors) <= 1:
        # No doors between these two rooms
        return door_index
    from_, to = map(list, zip(*from_to_doors))

    # randomly shuffle the door pairs
    shuffle(from_)
    shuffle(to)

    for from_, to in zip(from_, to):
        # remove the old mappings
        door_index.pop(from_)
        if from_ != to:
            door_index.pop(to)
        # add the shuffled mappings
        door_index[from_] = to
        door_index[to] = from_

    return door_index
