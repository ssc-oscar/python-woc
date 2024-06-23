#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-05-27

from typing import Iterable

from .local import WocMapsLocal


def format_map(key: str, map_objs: Iterable, level=1) -> str:
    # flatten the nested list
    while level > 1:
        map_objs = [item for sublist in map_objs for item in sublist]
        level -= 1
    return key + ";" + ";".join(map(str, map_objs))


if __name__ == "__main__":
    import argparse
    import logging
    import os
    import sys

    parser = argparse.ArgumentParser(description="Get record of various maps")
    parser.add_argument("type", type=str, help="The type of the object")
    parser.add_argument(
        "-p", "--profile", type=str, help="The path to the profile file", default=None
    )
    parser.add_argument(
        "-v", "--version", type=str, help="The version of the profile", default=None
    )
    args = parser.parse_args()

    woc = WocMapsLocal(args.profile, args.version)
    _level = 1
    if args.type == "b2tac":
        _level = 2
    for line in sys.stdin:
        try:
            key = line.strip()
            obj = woc.get_values(args.type, key)
            print(format_map(key, obj, _level))
        except BrokenPipeError:
            # ref: https://docs.python.org/3/library/signal.html#note-on-sigpipe
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)  # Python exits with error code 1 on EPIPE
        except Exception as e:
            logging.error(f"Error in {key}: {e}", exc_info=True)
            continue
