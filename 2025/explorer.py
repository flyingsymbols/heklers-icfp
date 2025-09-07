#!/usr/bin/env python3

import os
import json
import datetime
from random import randint
from pprint import pprint as pp

import requests
from requests_toolbelt.sessions import BaseUrlSession

from util import rel

PROBLEMS = {
    "probatio": 3,
    "primus": 6,
    "secundus": 12,
    "tertius": 18,
    "quartus": 24,
    "quintus": 30,
    "aleph": 12,
    "beth": 24,
    "gimel": 36,
    "daleth": 48,
    "he": 60,
    "vau": 18,
    "zain": 36,
    "hhet": 54,
    "teth": 72,
    "iod": 90,
}

def random_plan(length):
    """
    Generate a randomized plan that visits length doors
    """
    return "".join(str(randint(0, 5)) for _ in range(length))

def linear_plan(length, start=0, step=1):
    "should make sure that step is coprime with 6"
    return ''.join(str(n % 6) for n in range(start, start+length*step, step))

class Explorer:
    def __init__(self, id_, problem):
        self._id = id_
        self._problem = problem
        self._session = BaseUrlSession(
            "https://31pwr5t6ij.execute-api.eu-west-2.amazonaws.com/"
        )

    @classmethod
    def for_problem(cls, problem_name, id_=None):
        o = cls(id_, problem_name)
        res = o.start()
        print(res)
        num_rooms = o.number_of_rooms
        print(f'# Rooms: {num_rooms}')
        return o

    def write_example(self, name, **vars_):
        obj = {
            'problem': self._problem,
            'num_rooms': self.number_of_rooms,
            **vars_
        }

        tstamp = datetime.datetime.now().strftime('%d-%H%M%S')
        fname = f'{self._problem}-{name}-{tstamp}.json'
        fpath = rel('examples', fname)

        print(f'writing to {fpath}')
        with open(fpath, 'w') as f:
            json.dump(obj, f, indent=2)

    @property
    def number_of_rooms(self):
        """
        Based on the problem, return the number of rooms
        """
        return PROBLEMS[self._problem]

    def start(self):
        """
        Set up the problem "session"
        """
        return self._session.post(
            "/select",
            json={
                "id": self._id,
                "problemName": self._problem,
            },
        ).json()

    def get_random_plans(self, num_plans):
        """
        Get a random plan that uses the maximum allowable length, cause why not
        """
        return [random_plan(18 * self.number_of_rooms) for _ in range(num_plans)]

    def explore_all_linear(self):
        max_len = 18 * self.number_of_rooms
        plans = [linear_plan(max_len, n) for n in range(0,6)]
        pp(plans)
        res = self.explore(plans)
        new_results = []
        for r in res['results']:
            new_results.append(''.join(str(l) for l in r))
        res['results'] = new_results
        return {
            'input': plans, 
            'output': res
        }

    def explore(self, plans):
        """
        Explore with the plans and get back the results
        """
        return self._session.post(
            "/explore",
            json={
                "id": self._id,
                "plans": plans,
            },
        ).json()

    def guess(self, starting_room, door_pairs):
        """
        Submit a guess of the map
        """
        return self._session.post(
            "/guess",
            json={
                "id": self._id,
                "map": {
                    "rooms": list(range(self.number_of_rooms)),
                    "startingRoom": starting_room,
                    "connections": [
                        {
                            "from": {
                                "room": src_room,
                                "door": src_door,
                            },
                            "to": {
                                "room": dest_room,
                                "door": dest_door,
                            },
                        }
                        for src_room, src_door, dest_room, dest_door in door_pairs
                    ],
                },
            },
        )
