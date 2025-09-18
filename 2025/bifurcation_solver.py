"""
Terminology: 

room: the true identity of a room in the aedificium
hint: the 2 bit hint of the room number - several rooms can share the same 2 bit hint
starting_room: the start room is ALWAYS the same, which is useful for the next thing...
path: a starting subset of a plan that uniquely identifies the room you reach. Traversing the same path is guaranteed to reach the same room.
archetype: once we've identified the different rooms, we'll have a `(hint, door): next_hint` "shape" that can be used to identify that room in the future (among its identically hinted peers)

The idea is that as we process plan/result, we will visit the same "hint" multiple times, and if we ever see the same (hint, door) lead to a different next_hint room, we know the two paths leading to "hint" must refer to different rooms.

We track all collisions until we find a door that collides for all muliples of the hint less than the total number of rooms in the aedificium. So for example in Primus we have 6 rooms, meaning 2 will be unique and 4 will be paired dups. If we see (room 3, door 4): room 1 and then later (room 3, door 4): room 2 , we can conclude that these must be different rooms.
"""


from functools import cache
from rich.console import Console
from rich.table import Table


def get_hint(room):
    return room & 3

class BifurcationSolver:
    def __init__(self, explorer):
        self.number_of_rooms = explorer.number_of_rooms
        self.explorer = explorer
        self.starting_room = None
        self._hint_door_index = {}

    def _update_indexes(self, path, hint, door, next_hint):
        # We guess that the room IS the hint
        room = hint
        while True:
            if room not in self._hint_door_index:
                # hint: (path, next_hint)
                self._hint_door_index[room] = {} #door:(path, next_room)}
            if door not in self._hint_door_index[room]:
                # If it's the first time we've seen this particular door for this hint, save it
                self._hint_door_index[room][door] = (path, next_hint)
                return # first instance of room, door
            existing_path, existing_next_hint = self._hint_door_index[room][door]
            if existing_next_hint == next_hint:
                # If we've seen this hint, door before, and it's the same, update if the path is shorter
                if len(path) < len(existing_path):
                    # prefer the shortest path to this room
                    self._hint_door_index[room][door] = (path, next_hint)
                return
            else:
                # Otherwise this must be a different room!
                room += 4 # this path is a new room!

    def _add_plan_result(self, plan, result):
        current_path = ""
        # this should be the same each time
        if not self.starting_room:
            self.starting_room = result.pop(0)
        else:
            result.pop(0)
        current_hint = self.starting_room
        for door, next_hint in zip(plan, result):
            self._update_indexes(current_path, current_hint, door, next_hint)
            if self._found_all_rooms():
                return
            current_path += door
            current_hint = next_hint

    def _found_all_rooms(self):
        return len(self._hint_door_index) == self.number_of_rooms

    @cache
    def _get_archetype_doors(self):
        """
        Each room has experienced collisions on a door, until finally we collide for a
        single door across all rooms of that hint. Therefore, we need to know for each
        hint which door we should check to distinguish among them
        """
        archetype_doors = [None for _ in range(4)]
        for archetype_room in range(self.number_of_rooms)[-4:]:
            door, _ = next(x for x in self._hint_door_index[archetype_room].items())
            archetype_doors[get_hint(archetype_room)] = door
        return archetype_doors

    @cache
    def _get_room_archetype_lookup(self):
        """
        Knowing which door we should check for each hint, we also need to know the expected
        next_hint on the other side of the door for each room number

        room_archetype_lookup takes a (hint, door, hint) and tells you which room it is, assuming
        you're using the correct door for that hint archetype
        """
        room_archetype_lookup = {}
        archetype_doors = self._get_archetype_doors()
        for room, doors in self._hint_door_index.items():
            # For each archetype, get the door we should be checking
            door = archetype_doors[get_hint(room)]
            # Check this one distinguishing door to find the relevant info
            _, next_hint = doors[door]
            # (path, shape) where shape is (get_hint(room), door, next_hint)
            room_archetype_lookup[(get_hint(room), door, next_hint)] = room
        return room_archetype_lookup

    @cache
    def _get_room_paths(self):
        """
        We have one known path for each room number
        """
        room_paths = {}
        archetype_doors = self._get_archetype_doors()
        for room, doors in self._hint_door_index.items():
            door = archetype_doors[get_hint(room)]
            path, _ = doors[door]
            room_paths[room] = path
        return room_paths


    def solve(self):
        console = Console()

        console.print("Randomly exploring with random maximum length plans")
        while not self._found_all_rooms():
            plans = self.explorer.get_random_plans(self.number_of_rooms * 100)
            console.print(f"Exploring {self.number_of_rooms * 100} plans...")
            response = self.explorer.explore(plans)
            query_count = response["queryCount"]
            console.print(f"Query count is: {query_count}")
            for plan, result in zip(plans, response["results"]):
                self._add_plan_result(plan, result)

        # At this point we have 3 things:

        # 1. a unique path for each room
        room_paths = self._get_room_paths()

        # 2. a door per "hint" that can be used to tell rooms with the same hint apart
        archetype_doors = self._get_archetype_doors()


        # 3. a distinguishing (hint, door, next_hint) "shape" for each room
        room_archetype_lookup = self._get_room_archetype_lookup()

        console.print("Success! We found the following unique rooms:")
        table = Table(title="Unique Rooms")

        table.add_column("room")
        table.add_column("archetype")
        table.add_column("door path")

        reverse_lookup = {value: key for key, value in room_archetype_lookup.items()}

        for room in range(self.number_of_rooms):
            table.add_row(str(room), str(reverse_lookup[room]), f'"{room_paths[room]}"')

        console.print(table)


        # So the first thing we need to do is hit each door for the unique room paths (one plan per door)

        console.print("Now we need to visit each door of each of these unique rooms to find out what 'hint' is on the other side")

        # plan out a visit to each of these rooms' doors
        plans = []
        for room in range(self.number_of_rooms):
            path = room_paths[room]
            for door in range(6):
                # plans are ordered by room, door, so results will be too
                plans.append(path + str(door))

        results = self.explorer.explore(plans)["results"] # last item in the result is the "hint" of the room beyond (room, door)

        # find out what hint is on the side of each door
        room_door_hint = {}
        for room in range(self.number_of_rooms):
            for door in range(6):
                # save off the "hint" for the room we find through (room, door)
                room_door_hint[(room, door)] = results[room * 6 + door][-1]

        console.print("Visited all the doors on the other side and found the following:")

        table = Table(title="From the real rooms, doors lead to hints")

        table.add_column("room")
        table.add_column("door")
        table.add_column("next_hint")

        for (room, door), hint in room_door_hint.items():
            table.add_row(str(room), str(door), str(hint))

        console.print(table)

        # plan out a visit to the proper door based on the archetype of the room hint so we can
        plans = []
        for room in range(self.number_of_rooms):
            path = room_paths[room]
            for door in range(6):
                hint = room_door_hint[(room, door)]
                # visit the current room, take each door, then take the archetype door appropriate for the hint of that next room
                plans.append(path + str(door) + str(archetype_doors[hint]))

        console.print("Based on the room 'archetypes' before, we know which door to check based on the 'hint' to find out which room it actually is")

        results = self.explorer.explore(plans)["results"]

        # calculate the actual room number of the other side of each door based on the archetype
        room_door_room = {}
        for (room, door), hint in room_door_hint.items():
            next_hint = results[room * 6 + door][-1]
            room_door_room[(room, door)] = room_archetype_lookup[(hint, str(archetype_doors[hint]), next_hint)]

        console.print("Finally, we found the true room numbers for each of these hints")

        table = Table(title="(room, door) to room")

        table.add_column("room")
        table.add_column("door")
        table.add_column("next_room")

        for (room, door), next_room in room_door_room.items():
            table.add_row(str(room), str(door), str(next_room))

        console.print(table)

        console.print("The last step is to randomly match doors between pairs of connected rooms to make the 'connections' required by the guess")

        door_pairs = []
        for src_room in range(self.number_of_rooms):
            for dest_room in range(self.number_of_rooms):
                src_to_dest = [
                    (room, door) for (room, door), next_room in room_door_room.items() if room == src_room and next_room == dest_room
                ]
                dest_to_src = [
                    (room, door) for (room, door), next_room in room_door_room.items() if room == dest_room and next_room == src_room
                ]

                for (src_room, src_door), (dest_room, dest_door) in zip(
                    src_to_dest, dest_to_src
                ):
                    door_pairs.append((src_room, src_door, dest_room, dest_door))

        console.print("All that's left to do is guess!")
        print(self.explorer.guess(0, door_pairs))

        # finally, find the connections by randomly matching pairs
        print("done!")

