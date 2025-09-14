"""
Test that the hintify operation ignores variants but does not ignore invariants of AEdificium maps
"""

from .conftest import door_index_to_guess, shuffle_all_door_mappings, shuffle_rooms


def test_door_swap_hintify(problem):
    """
    Verify that AEdificium maps with door pair variants and room number variants are still accepted as correct
    """
    # shuffle room numbers in a way that preserves the 2 bit hint
    door_index = shuffle_rooms(problem.door_index, 3)

    # swap some pairs of doors such that they still connect the same two rooms
    door_index = shuffle_all_door_mappings(door_index, 3)

    assert problem.guess(
        door_index_to_guess(door_index, 3)
    ), "The door mappings were not treated agnostically!"
