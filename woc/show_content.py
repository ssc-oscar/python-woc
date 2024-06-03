#!/usr/bin/env python3

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-05-27

from .local import WocMapsLocal

def format_tree(tree_objs: list) -> str:
    _out = ''
    for line in tree_objs:
        _out += f'{line[0]};{line[2]};{line[1]}\n'
    return _out

def format_commit(sha: str, cmt: str, format: int = 0): 
    if format == 3: # raw
        return cmt
    
    if format == 7: # commit sha; base64(raw)
        import base64
        _b64 = base64.b64encode(cmt.encode()).decode()
        # mock linux's base64, add newline every 76 characters
        _b64 = '\\n'.join([_b64[i:i+76] for i in range(0, len(_b64), 76)]) + '\\n'
        return sha + ';' + _b64

    lines = cmt.split('\n')
    tree_sha = lines[0][5:]

    if lines[1].startswith('parent'):
        parent_sha = lines[1][7:]
    else:
        # insert a dummy line
        lines.insert(1, '')
        parent_sha = ''

    author_idx = lines[2].find('>')
    author = lines[2][7:author_idx+1]
    author_time = lines[2][author_idx+2:]
    author_timestamp = author_time.split(' ')[0]
    author_timezone = author_time.split(' ')[1]

    committer_idx = lines[3].find('>')
    committer = lines[3][10:committer_idx+1]
    committer_time = lines[3][committer_idx+2:]
    committer_timestamp = committer_time.split(' ')[0]
    committer_timezone = committer_time.split(' ')[1]

    commit_msg = '\\n'.join(lines[5:])
    if commit_msg.endswith('\\n'): # strip
        commit_msg = commit_msg[:-2]

    if format == 0: # commit SHA;tree SHA;parent commit SHA;author;committer;author timestamp;commit timestamp
        return ';'.join([sha, tree_sha, parent_sha, author, committer, author_timestamp, committer_timestamp])
    
    elif format == 1: # commit SHA;author timestamp;author
        return ';'.join([sha, author_timestamp, author])

    elif format == 2: # commit SHA;author;author timestamp; author timezone;commit message
        return ';'.join([sha, author, author_timestamp, author_timezone, commit_msg])
    
    elif format == 4: # commit SHA;author
        return ';'.join([sha, author])

    elif format == 5: # commit SHA; parent commit SHA
        return ';'.join([sha, parent_sha])

    elif format == 6: # commit SHA;author timestamp;author timezone;author;tree sha;parent sha
        return ';'.join([sha, author_timestamp, author_timezone, author, tree_sha, parent_sha])

    elif format == 8: # commit sha; author timestamp; commit timestamp; author; committer; parent sha
        return ';'.join([sha, author_timestamp, committer_timestamp, author, committer, parent_sha])

    elif format == 9: # commit sha; tree sha; parent sha; author; committer; author timestamp; commit timestamp; author timezone; committer timezone; commit message
        return ';'.join([sha, tree_sha, parent_sha, author, committer, author_timestamp, committer_timestamp, author_timezone, committer_timezone, commit_msg])

    else:
        raise ValueError(f'Invalid format {format}')
    

if __name__ == '__main__':
    import argparse
    import logging
    import sys
    import os

    parser = argparse.ArgumentParser(description='See the Content of Git Object', usage='echo <key> | %(prog)s type (format)')
    parser.add_argument('type', type=str, help='The type of the object')
    parser.add_argument('format', type=int, help='The format of the object', default=0, nargs='?')
    args = parser.parse_args()

    woc = WocMapsLocal()
    for line in sys.stdin:
        try:
            key = line.strip()
            obj = woc.show_content(args.type, key)
            if args.type == 'commit':
                print(format_commit(key, obj, args.format))
            elif args.type == 'tree':
                print(format_tree(obj))
            elif args.type == 'blob':
                print(obj)
            else:
                raise ValueError(f'Invalid object type {args.type}')
        except BrokenPipeError:
            # ref: https://docs.python.org/3/library/signal.html#note-on-sigpipe
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
            sys.exit(1) # Python exits with error code 1 on EPIPE
        except Exception as e:
            logging.error(f'Error in {key}: {e}', exc_info=True)
            continue