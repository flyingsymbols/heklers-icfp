#!/usr/bin/env python3

import os
import json
import typing
import datetime
from enum import Enum
from pathlib import Path

import rich
import typer
from pydantic import BaseModel

class InOutPairs(BaseModel):
    problem: str
    num_rooms: int
    input: typing.List[str]
    output: 'ExploreResponseStrs'

    @classmethod
    def load(cls, json_fpath: Path):
        with open(json_fpath, 'r') as f:
            obj = json.load(f)

        return InOutPairs(**obj)

class ExploreResponseStrs(BaseModel):
    results: typing.List[str]
    queryCount: int

class LabelSets(BaseModel):
    num_rooms: int
    label_map: typing.Dict['RoomLabel', 'LabelClasses']

    @classmethod
    def for_rooms(cls, num_rooms):
        label_map = {
            RoomLabel(str(i)): LabelClasses(
                paths_to_labelmaps={}, min_classes=0, max_classes=num_rooms
            ) for i in range(4)
        }

        return cls(num_rooms=num_rooms, label_map=label_map)

class LabelClasses(BaseModel):
    paths_to_labelmaps: typing.Dict['DoorList', 'LabelMap']
    min_classes: int
    max_classes: int

class LabelMap(BaseModel):
    paths_to_labels: typing.Dict['DoorPath', 'Door']
    first_path: 'DoorPath'

DoorList = typing.NewType('DoorList', str)
DoorPath = typing.NewType('DoorPath', str) # used to index

class RoomLabel(str, Enum):
    L0 = '0'
    L1 = '1'
    L2 = '2'
    L3 = '3'

class Door(str, Enum):
    D0 = '0'
    D1 = '1'
    D2 = '2'
    D3 = '3'
    D4 = '4'
    D5 = '5'

def show(x):
    rich.print(x)

if __name__ == '__main__':
    main()
