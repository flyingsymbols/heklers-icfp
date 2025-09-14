"""
A ProblemSession is a live instance of a problem that is being explored
and hopefully solved
"""

import secrets

from fastapi import HTTPException
from pydantic import BaseModel, Field

LIGHTNING_PROBLEMS = {
    "probatio": 3,
    "primus": 6,
    "secundus": 12,
    "tertius": 18,
    "quartus": 24,
    "quintus": 30,
}

PROBLEMS = LIGHTNING_PROBLEMS


class RoomDoorField(BaseModel):
    """
    room/door pair
    """

    room: int
    door: int


class ConnectionField(BaseModel):
    """
    From room/door to room/door
    """

    from_: RoomDoorField = Field(alias="from")
    to: RoomDoorField


class MapField(BaseModel):
    """
    This is a serialized map of an AEdificium
    """

    rooms: list[int]
    startingRoom: int
    connections: list[ConnectionField]


def get_room_hint(room_number):
    """
    Return 2 bits of information about the room number
    """
    return room_number & 3


def hintify(door_index):
    """
    This produces a data structure that can be used to determine if two door_indexes refer
    to the same set of rooms.

    1. If two rooms are connected by more than one pair of doors, we don't care which they matched, so just group them
    2. If they misnumbered the rooms, we don't care - hintify the room numbers
    3. Need to be sorted by invariants so that solutions are unique
    4. Ensure we're tuplified so we can directly compare equality
    """

    # first, combine all doors between two rooms into a single to/from listing
    aggregation_map = {}
    for (from_room, from_door), (to_room, _) in door_index.items():
        if (from_room, to_room) not in aggregation_map:
            aggregation_map[(from_room, to_room)] = []
        aggregation_map[(from_room, to_room)].append(from_door)

    # second, hintify the room names and sort doors
    anonymized_list = []
    for (from_room, to_room), doors in aggregation_map.items():
        # (fourth) tuplify the listing
        anonymized_list.append(
            ((get_room_hint(from_room), get_room_hint(to_room)), tuple(sorted(doors)))
        )

    # third, sort the whole thing by (now) invariants
    return sorted(anonymized_list)


class ProblemSession:
    """
    A problem session is a single instance of a problem that is being solved
    """

    def __init__(self, problem_name):
        if problem_name not in PROBLEMS:
            raise HTTPException(status_code=404, detail="No problem by that name")
        self.problem_name = problem_name
        self.number_of_rooms = PROBLEMS[problem_name]
        self.query_count = 0
        door_index = {}

        doors_to_be_matched = [
            (room, door) for room in range(self.number_of_rooms) for door in range(6)
        ]

        while doors_to_be_matched:
            # select 2 "with replacement" so that we can end up with a door linking to itself
            door1 = secrets.choice(doors_to_be_matched)
            door2 = secrets.choice(doors_to_be_matched)

            # add to/from mappings
            door_index[door1] = door2
            door_index[door2] = door1

            # remove door1, and if it's not the same door, remove door2
            doors_to_be_matched.remove(door1)
            if door1 != door2:
                doors_to_be_matched.remove(door2)

        self.door_index = door_index
        # for efficiency precalculate the hintified version of this graph for evaulating solutions
        self.hintified = hintify(door_index)

    def explore_all(self, plans) -> list[list[int]]:
        """
        Explore many plans at once, penalizing an additional query_count for the request
        """
        if any(len(plan) > (18 * self.number_of_rooms) for plan in plans):
            raise HTTPException(
                status_code=422, detail="plans cannot be longer than 18n"
            )
        self.query_count += 1
        return [self.explore(plan) for plan in plans]

    def explore(self, plan) -> list[int]:
        """
        Explore a single plan, incrementing query_count
        """
        plan = map(int, plan)
        current_room = 0
        result = [current_room]

        for door in plan:
            current_room, _ = self.door_index[(current_room, door)]
            result.append(get_room_hint(current_room))

        self.query_count += 1
        return result

    def guess(self, room_map: MapField) -> bool:
        """
        Accept a guess in the form of a MapField
        """
        if room_map.startingRoom != 0:
            return False
        if self.number_of_rooms != len(room_map.rooms):
            return False
        if not set(range(self.number_of_rooms)) == set(room_map.rooms):
            return False
        door_index = {
            (connection.from_.room, connection.from_.door): (
                connection.to.room,
                connection.to.door,
            )
            for connection in room_map.connections
        }

        door_index.update(
            {
                (connection.to.room, connection.to.door): (
                    connection.from_.room,
                    connection.from_.door,
                )
                for connection in room_map.connections
            }
        )

        return hintify(door_index) == self.hintified
