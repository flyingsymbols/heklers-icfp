#!/usr/bin/env python3

import requests


class LibraryApi:
    def __init__(self, id):
        self.base_url = "https://31pwr5t6ij.execute-api.eu-west-2.amazonaws.com/"
        self.id = id

    def register(self, team_name, preferred_language, email):
        return requests.post(
            f"{self.base_url}/register",
            json={
                "name": team_name,
                "pl": preferred_language,
                "email": email,
            },
        ).json()

    def select(self, problem_name):
        return requests.post(
            f"{self.base_url}/select", json={"id": self.id, "problemName": problem_name}
        ).json()

    def explore(self, plans):
        return requests.post(
            f"{self.base_url}/explore", json={"id".self.id, "plans", plans}
        ).json()

    def guess(self, map):
        return requests.post(
            f"{self.base_url}/guess", json={"id": self.id, "map": map}
        ).json()


def main():
    pass


if __name__ == "__main__":
    main()
