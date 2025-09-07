#!/usr/bin/env python3
"""
This was the script used for registration
"""

import requests

def register(team_name, preferred_language, email):
    return requests.post(
        "https://31pwr5t6ij.execute-api.eu-west-2.amazonaws.com/register",
        json={
            "name": team_name,
            "pl": preferred_language,
            "email": email,
        }
    ).json()
