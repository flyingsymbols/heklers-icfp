"""
Shared utils
"""

import subprocess
import os

DIRNAME = os.path.dirname(__file__)

def rel(*path):
    """
    create an absolute path relative to this file
    """
    return os.path.join(DIRNAME, *path)


def door_dir(door):
    """
    Return the compass direction associated with a door for attaching an edge to the right
    compass position on a node, see graphviz docs
    """
    door = str(door)
    return {
        "0": "ne",
        "1": "se",
        "2": "s",
        "3": "sw",
        "4": "nw",
        "5": "n",
    }[door]
