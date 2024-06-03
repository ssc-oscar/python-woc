#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-05-27

from typing import Iterable
from .local import WocMapsLocal

def format_map(key: str, map_objs: Iterable) -> str:
    return key + ';' + ';'.join(map(str, map_objs))

if __name__ == '__main__':
    import argparse
    import sys
    import os
    import logging

    parser = argparse.ArgumentParser(description='Get record of various maps')
    parser.add_argument('type', type=str, help='The type of the object')
    # key is taken from stdin
    parser.add_argument('key', type=str, help='The key of the object', nargs='?')
    args = parser.parse_args()
    if not args.key:
        args.key = sys.stdin.readline()
    args.key = args.key.strip()

    woc = WocMapsLocal()
    for line in sys.stdin:
        try:
            key = line.strip()
            obj = woc.get_values(args.type, args.key)
            print(format_map(args.key, obj))
        except BrokenPipeError:
            # ref: https://docs.python.org/3/library/signal.html#note-on-sigpipe
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1) # Python exits with error code 1 on EPIPE
        except Exception as e:
            logging.error(f'Error in {key}: {e}', exc_info=True)
            continue