#!/usr/bin/env python3

from LibraryApi import LibraryApi


def main():
    lib_api = LibraryApi()
    lib_api.select("probatio")
    print(lib_api.explore(plans=["123"]))


if __name__ == "__main__":
    main()
