#!/usr/bin/env python3

from explorer import Explorer
from aedificium_trusted_room_graph import AEdificiumTrustedRoomGraph

from secret import ID

def main():
    explorer = Explorer(ID, "probatio")
    explorer.start()
    plans = explorer.get_random_plans(explorer.number_of_rooms * 4)

    print("Our plan is:")
    print(plans)
    print("\n")
    response = explorer.explore(plans)

    graph = AEdificiumTrustedRoomGraph(number_of_rooms=explorer.number_of_rooms)

    print("The results we got were:")
    print(response)
    print("\n")
    for plan, result in zip(plans, response["results"]):
        graph.add_plan_result(plan, result)

    if graph.is_complete():
        print("WE WIN")
        print(
            explorer.guess(
                graph.starting_room,
                graph.get_door_pairs(),
            ).json()
        )
    else:
        print("WE LOSE: there wasn't enough info to solve")

if __name__ == "__main__":
    main()
