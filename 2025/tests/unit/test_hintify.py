from copy import deepcopy

from .conftest import problem, shuffle_rooms, shuffle_all_door_mappings, door_index_to_guess


def test_door_swap_hintify(problem):
    # shuffle room numbers in a way that preserves the 2 bit hint
    door_index = shuffle_rooms(problem.door_index, 3)

    # swap some pairs of doors such that they still connect the same two rooms
    door_index = shuffle_all_door_mappings(door_index, 3)

    assert problem.guess(door_index_to_guess(door_index, 3)), "The door mappings were not treated agnostically!"


