"""
The AEdificium Trusted Room Graph assumes that room numbers identify each room uniquely.
This is only true for the Probatio problem and so it should not be used on other problems
"""

import graphviz

from util import door_dir


class AEdificiumTrustedRoomGraph:
    """
    The Total graph assumes that the room numbers are the true room numbers
    """
    def __init__(self, number_of_rooms):
        self._rooms = {}
        self._number_of_rooms = number_of_rooms
        self._starting_room = None

    @property
    def starting_room(self):
        """
        This is the room we start in, from results
        """
        return self._starting_room

    def add_plan_result(self, plan, result):
        """
        Interpret a plan and its results as nodes and edges in a directed graph
        Each door we go through gets us to a new room, but we don't know the door we came in :'(
        """
        plan = map(int, plan)
        current_room = result.pop(0)
        # this should be the same each time
        self._starting_room = current_room
        for door, room in zip(plan, result):
            if current_room not in self._rooms:
                self._rooms[current_room] = {}
            self._rooms[current_room][door] = room
            current_room = room

    def show_directed(self):
        """
        Use this for partial room maps where we don't know all the doors yet

        The head (arrow) is not pointed at a door slot because we don't know it
        """
        dot = graphviz.Digraph(comment="AEdificium", format="png")
        seen = set()
        for room, doorways in self._rooms.items():
            if room not in seen:
                dot.node(str(room), str(room), shape="hexagon")
                seen.add(room)
            for door, dest_room in doorways.items():
                if dest_room not in seen:
                    dot.node(str(dest_room), str(dest_room), shape="hexagon")
                    seen.add(dest_room)
                dot.edge(f"{room}:{door_dir(door)}", str(dest_room))
        dot.render("aedificium", view=True)

    def get_door_pairs(self):
        """
        Get the door pairs that connect the rooms where each entry in the list is:
            (src_room, src_door, dest_room, dest_door)
        """
        # get all unique pairs of rooms including self pairs
        room_pairs = []
        for i in range(self._number_of_rooms):
            for j in range(i, self._number_of_rooms):
                room_pairs.append((i, j))

        # for rooms that link to each other, match up pairs of doors arbitrarily
        door_pairs = []
        for src, dest in room_pairs:
            # src/dest can be the same room
            src_to_dest = [
                (src, door) for door, d in self._rooms[src].items() if d == dest
            ]
            dest_to_src = [
                (dest, door) for door, s in self._rooms[dest].items() if s == src
            ]

            for (src_room, src_door), (dest_room, dest_door) in zip(
                src_to_dest, dest_to_src
            ):
                door_pairs.append((src_room, src_door, dest_room, dest_door))

        return door_pairs

    def is_complete(self):
        """
        Check to see if we have total information
        """
        if len(self._rooms) < self._number_of_rooms:
            return False
        for room, doors in self._rooms.items():
            if len(doors) < 6:
                return False
        return True

    def show(self):
        """
        Use this to see the total map of the library (door numbers omitted for clarity)
        """
        door_pairs = self.get_door_pairs()
        dot = graphviz.Digraph(comment="AEdificium", format="png")
        seen = set()
        for src_room, src_door, dest_room, dest_door in door_pairs:
            if src_room not in seen:
                dot.node(str(src_room), str(src_room), shape="hexagon")
                seen.add(src_room)
            if dest_room not in seen:
                dot.node(str(dest_room), str(dest_room), shape="hexagon")
                seen.add(dest_room)
            dot.edge(
                f"{src_room}:{door_dir(src_door)}",
                f"{dest_room}:{door_dir(dest_door)}",
                # taillabel=str(src_door),
                # headlabel=str(dest_door),
                arrowhead="none",
                arrowtail="none",
            )
        dot.render("aedificium", view=True)
