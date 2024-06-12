#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-05-27

from .local import WocMapsLocal, decode_commit, decode_str, decomp_or_raw


def format_tree(tree_objs: list) -> str:
    _out = ""
    for line in tree_objs:
        _out += f"{line[0]};{line[2]};{line[1]}\n"
    return _out


def format_commit(sha: str, cmt_bin: bytes, format: int = 0):
    if format == 3:  # raw
        cmt = decode_str(cmt_bin)
        return cmt

    if format == 7:  # commit sha; base64(raw)
        import base64

        _b64 = base64.b64encode(cmt_bin).decode()
        # mock linux's base64, add newline every 76 characters
        _b64 = "\\n".join([_b64[i : i + 76] for i in range(0, len(_b64), 76)]) + "\\n"
        return sha + ";" + _b64

    (
        tree_sha,
        parents,
        (author, author_timestamp, author_timezone),
        (committer, committer_timestamp, committer_timezone),
        commit_msg,
    ) = decode_commit(cmt_bin)
    parent_sha = parents[0]  # only the first parent

    if (
        format == 0
    ):  # commit SHA;tree SHA;parent commit SHA;author;committer;author timestamp;commit timestamp
        return ";".join(
            [
                sha,
                tree_sha,
                parent_sha,
                author,
                committer,
                author_timestamp,
                committer_timestamp,
            ]
        )

    elif format == 1:  # commit SHA;author timestamp;author
        return ";".join([sha, author_timestamp, author])

    elif (
        format == 2
    ):  # commit SHA;author;author timestamp; author timezone;commit message
        return ";".join([sha, author, author_timestamp, author_timezone, commit_msg])

    elif format == 4:  # commit SHA;author
        return ";".join([sha, author])

    elif format == 5:  # commit SHA; parent commit SHA
        return ";".join([sha, parent_sha])

    elif (
        format == 6
    ):  # commit SHA;author timestamp;author timezone;author;tree sha;parent sha
        return ";".join(
            [sha, author_timestamp, author_timezone, author, tree_sha, parent_sha]
        )

    elif (
        format == 8
    ):  # commit sha; author timestamp; commit timestamp; author; committer; parent sha
        return ";".join(
            [sha, author_timestamp, committer_timestamp, author, committer, parent_sha]
        )

    elif (
        format == 9
    ):  # commit sha; tree sha; parent sha; author; committer; author timestamp; commit timestamp; author timezone; committer timezone; commit message
        return ";".join(
            [
                sha,
                tree_sha,
                parent_sha,
                author,
                committer,
                author_timestamp,
                committer_timestamp,
                author_timezone,
                committer_timezone,
                commit_msg,
            ]
        )

    else:
        raise ValueError(f"Invalid format {format}")


if __name__ == "__main__":
    import argparse
    import logging
    import os
    import sys

    parser = argparse.ArgumentParser(
        description="See the Content of Git Object",
        usage="echo <key> | %(prog)s type (format)",
    )
    parser.add_argument("type", type=str, help="The type of the object")
    parser.add_argument(
        "format", type=int, help="The format of the object", default=0, nargs="?"
    )
    parser.add_argument(
        "-p", "--profile", type=str, help="The path to the profile file", default=None
    )
    args = parser.parse_args()

    woc = WocMapsLocal(args.profile)
    for line in sys.stdin:
        try:
            key = line.strip()
            if args.type == "commit":
                obj_bin = decomp_or_raw(woc._get_tch_bytes(args.type, key)[0])
                print(format_commit(key, obj_bin, args.format))
            elif args.type == "tree":
                obj = woc.show_content(args.type, key)
                print(format_tree(obj))
            elif args.type == "blob":
                obj = woc.show_content(args.type, key)
                print(obj)
            else:
                raise ValueError(f"Invalid object type {args.type}")
        except BrokenPipeError:
            # ref: https://docs.python.org/3/library/signal.html#note-on-sigpipe
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1)  # Python exits with error code 1 on EPIPE
        except Exception as e:
            logging.error(f"Error in {key}: {e}", exc_info=True)
            continue
