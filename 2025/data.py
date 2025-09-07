#!/usr/bin/env python3

import os
import json
import typing
import datetime
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

def show(x):
    rich.print(x)

if __name__ == '__main__':
    main()
