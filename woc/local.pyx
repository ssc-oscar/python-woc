# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False, profile=True, linetrace=True
# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-01-17

import os
import json
import logging
import time
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from threading import Lock
from typing import Tuple, Dict, Iterable, List, Union, Literal, Optional
import gzip

try:
    import lzf
    assert lzf.decompress
except ImportError or AssertionError:
    raise ImportError('python-lzf is required to decompress LZF-compressed data: `pip install python-lzf`')

from .base import WocMapsBase, WocObjectsWithContent, WocSupportedProfileVersions
from .tch cimport TCHashDB

logger = logging.getLogger(__name__)
    
### Utility functions ###

cpdef uint32_t fnvhash(bytes data):
    """
    Returns the 32 bit FNV-1a hash value for the given data.
    >>> hex(fnvhash('foo'))
    '0xa9f37ed7'
    """
    # PY: 5.8usec Cy: 66.8ns
    cdef:
        uint32_t hval = 0x811c9dc5
        uint8_t b
    for b in data:  
        hval ^= b
        hval *= 0x01000193
    return hval

cpdef unber(bytes buf):
    r""" Perl BER unpacking.
    BER is a way to pack several variable-length ints into one
    binary string. Here we do the reverse.
    Format definition: from http://perldoc.perl.org/functions/pack.html
        (see "w" template description)

    Args:
        buf (bytes): a binary string with packed values

    Returns:
         str: a list of unpacked values

    >>> unber(b'\x00\x83M')
    [0, 461]
    >>> unber(b'\x83M\x96\x14')
    [461, 2836]
    >>> unber(b'\x99a\x89\x12')
    [3297, 1170]
    """
    # PY: 262ns, Cy: 78ns
    cdef:
        list res = []
        # blob_offset sizes are getting close to 32-bit integer max
        uint64_t acc = 0  
        uint8_t b

    for b in buf:
        acc = (acc << 7) + (b & 0x7f)
        if not b & 0x80:
            res.append(acc)
            acc = 0  
    return res

cpdef (int, int) lzf_length(bytes raw_data):
    r""" Get length of uncompressed data from a header of Compress::LZF
    output. Check Compress::LZF sources for the definition of this bit magic
        (namely, LZF.xs, decompress_sv)
        https://metacpan.org/source/MLEHMANN/Compress-LZF-3.8/LZF.xs

    Args:
        raw_data (bytes): data compressed with Perl Compress::LZF

    Returns:
         Tuple[int, int]: (header_size, uncompressed_content_length) in bytes

    >>> lzf_length(b'\xc4\x9b')
    (2, 283)
    >>> lzf_length(b'\xc3\xa4')
    (2, 228)
    >>> lzf_length(b'\xc3\x8a')
    (2, 202)
    >>> lzf_length(b'\xca\x87')
    (2, 647)
    >>> lzf_length(b'\xe1\xaf\xa9')
    (3, 7145)
    >>> lzf_length(b'\xe0\xa7\x9c')
    (3, 2524)
    """
    # PY:725us, Cy:194usec
    cdef:
        # compressed size, header length, uncompressed size
        uint32_t csize=len(raw_data), start=1, usize
        # first byte, mask, buffer iterator placeholder
        uint8_t lower=raw_data[0], mask=0x80, b

    while mask and csize > start and (lower & mask):
        mask >>= 1 + (mask == 0x80)
        start += 1
    if not mask or csize < start:
        raise ValueError('LZF compressed data header is corrupted')
    usize = lower & (mask - 1)
    for b in raw_data[1:start]:
        usize = (usize << 6) + (b & 0x3f)
    if not usize:
        raise ValueError('LZF compressed data header is corrupted')
    return start, usize

def decomp(bytes raw_data):
    # type: (bytes) -> bytes
    """ lzf wrapper to handle perl tweaks in Compress::LZF
    This function extracts uncompressed size header
    and then does usual lzf decompression.

    Args:
        raw_data (bytes): data compressed with Perl Compress::LZF

    Returns:
        str: unpacked data
    """
    if not raw_data:
        return b''
    if raw_data[0] == 0:
        return raw_data[1:]
    start, usize = lzf_length(raw_data)
    # while it is tempting to include liblzf and link statically, there is
    # zero advantage comparing to just using python-lzf
    return lzf.decompress(raw_data[start:], usize)

def decomp_or_raw(bytes raw_data):
    """ Try to decompress raw_data, return raw_data if it fails"""
    try:
        return decomp(raw_data)
    except ValueError:
        return raw_data

def slice20(bytes raw_data):
    """ Slice raw_data into 20-byte chunks and hex encode each of them
    It returns tuple in order to be cacheable
    """
    if raw_data is None:
        return ()
    return tuple(raw_data[i:i + 20] for i in range(0, len(raw_data), 20))

def decode_str(bytes raw_data):
    """ Decode raw_data, detect the encoding if utf-8 fails """
    try:
        return raw_data.decode('utf-8')
    except UnicodeDecodeError:
        import chardet  # should be rarely used
        _encoding = chardet.detect(raw_data)['encoding']
        return raw_data.decode(_encoding, errors='replace')


### TCH helpers ###

# Pool of open TokyoCabinet databases to save few milliseconds on opening
cdef dict _TCH_POOL = {}  # type: Dict[str, TCHashDB]
TCH_LOCK = Lock()

cpdef get_tch(char *path):
    """ Cache Hash() objects """
    if path in _TCH_POOL:
        return _TCH_POOL[path]
    try:
        TCH_LOCK.acquire()
        # in multithreading environment this can cause race condition,
        # so we need a lock
        if path not in _TCH_POOL:
            # open database in read-only mode and allow concurrent access
            _TCH_POOL[path] = TCHashDB(path, ro=True)  
    finally:
        TCH_LOCK.release()
    return _TCH_POOL[path]

cpdef uint8_t get_shard(bytes key, uint8_t sharding_bits, bint use_fnv_keys):
    """ Get shard id """
    cdef uint8_t p
    if use_fnv_keys:
        p = fnvhash(key)  
    else:
        p = key[0]
    cdef uint8_t prefix = p & (2**sharding_bits - 1)
    return prefix

cpdef bytes get_from_tch(bytes key, list shards, int sharding_bits, bint use_fnv_keys):
    # not 100% necessary but there are cases where some tchs are miserably missing
    _shard = get_shard(key, sharding_bits, use_fnv_keys)
    _path = shards[_shard]
    assert _path and os.path.exists(_path), f"shard {_shard} not found at {_path}"
    return get_tch(
        shards[get_shard(key, sharding_bits, use_fnv_keys)].encode('utf-8')
    )[key]

### deserializers ###

def decode_value(
    value: bytes,
    out_dtype: str
):
    if out_dtype == 'h':  # type: list[str]
        return [value[i:i + 20].hex() for i in range(0, len(value), 20)]
    elif out_dtype == 'sh':  # type: tuple[str, str, str]
        buf0 = value[0:len(value)-21]
        cmt_sha = value[(len(value)-20):len(value)]
        (Time, Author) = decode_str(buf0).split(";")
        return (Time, Author, cmt_sha.hex())  
    elif out_dtype == 'cs3':  # type: list[tuple[str, str, str]]
        data = decomp(value)
        _splited = decode_str(data).split(";")
        return [
            (_splited[i],_splited[i+1],_splited[i+2])
            for i in range(0, len(_splited), 3)
        ] 
    elif out_dtype == 'cs':   # type: list[str]
        data = decomp(value)
        return [decode_str(v)
            for v in data.split(b';')
            if v and v != b'EMPTY'] 
    elif out_dtype == 's':  # type: list[str]
        return [decode_str(v)
            for v in value.split(b';')]
    elif out_dtype == 'r':  # type: list[str, int]
        _hex = value[:20].hex()
        _len = unber(value[20:])[0]
        return (_hex, _len)
    elif out_dtype == 'hhwww':
        raise NotImplemented
    raise ValueError(f'Unsupported dtype: {out_dtype}')


def decode_tree(
    value: bytes
) -> List[Tuple[str, str, str]]:
    """
    Decode a tree binary object into tuples
    Reference: https://stackoverflow.com/questions/14790681/
        mode   (ASCII encoded decimal)
        SPACE (\0x20)
        filename
        NULL (\x00)
        20-byte binary hash
    """
    _out_buf = []
    _file_buf = []
    _curr_buf = bytes()
    
    # TODO: current impl is not efficient, need to optimize
    i = 0
    while i < len(value):
        if value[i] == 0x20:
            _file_buf.append(decode_str(_curr_buf))
            _curr_buf = bytes()
        elif value[i] == 0x00:
            _file_buf.append(decode_str(_curr_buf))
            # take next 20 bytes as a hash
            _curr_buf = value[i+1:i+21]
            _file_buf.append(_curr_buf.hex())
            _out_buf.append(tuple(_file_buf))
            # clear buffers
            _file_buf = []
            _curr_buf = bytes()
            i += 20
        else:
            _curr_buf += bytes([value[i]])
        i += 1

    return _out_buf


def parse_commit(cmt: str) -> Dict[str, str]:
    """
    Parse commit objects into a dictionary
    """
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
        
    return dict(
        tree=tree_sha,
        parent=parent_sha,
        author=author,
        author_timestamp=author_timestamp,
        author_timezone=author_timezone,
        committer=committer,
        committer_timestamp=committer_timestamp,
        committer_timezone=committer_timezone,
        message=commit_msg,
    )


def read_large(path: str, dtype: str) -> bytes:
    """Read a *.large.* and return its content""" 
    if dtype == 'h':
        with open(path, 'rb') as f:
            f.seek(20) # 160 bits of SHA1
            return f.read()
    else:
        # use zlib to decompress
        with gzip.open(path, 'rb') as f:
            _uncompressed = f.read()
            # find first 256 bytes for b'\n', don't scan the whole document
            _idx = _uncompressed[:256].find(b'\n')
            if _idx > 0:
                return _uncompressed[_idx+1:]  # a2f
            return _uncompressed  # b2tac


class WocMapsLocal(WocMapsBase):
    def __init__(self, 
            profile_path: Union[str, Iterable[str], None] = None,
            version: Union[str, Iterable[str], None] = None
        ) -> None:
        # load profile
        if profile_path is None:
            profile_path = (
                "wocprofile.json",
                "~/.wocprofile.json",
                "/etc/wocprofile.json",
            )
        if isinstance(profile_path, str):
            profile_path = (profile_path, )

        for p in profile_path:
            _full_path = os.path.expanduser(p)
            if os.path.exists(_full_path):
                with open(_full_path) as f:
                    self.config = json.load(f)
                break
        else:
            raise FileNotFoundError("No wocprofile.json found in the following paths: {}, "
                                    "run `python3 -m woc.detect` to generate".format(profile_path))

        # check profile
        assert self.config["wocSchemaVersion"] in WocSupportedProfileVersions, \
                                    "Unsupported wocprofile version: {}".format(self.config["wocSchemaVersion"])
        assert self.config["maps"], "Run `python3 -m woc.detect` to scan data files and generate wocprofile.json"

    def get_values(
        self,
        map_name: str,
        key: Union[bytes, str],
    ):
        """Eqivalent to getValues in WoC Perl API
        >>> get_values('P2c', 'user2589_minicms')  # doctest: +SKIP
        ...
        """

        if map_name in self.config["maps"]:
            _map = self.config["maps"][map_name][0]
        elif map_name in self.config["objects"]:
            _map = self.config["objects"][map_name]
        else:
            raise KeyError(f'Invalid map name: {map_name}, '
                f'expect one of {", ".join(self.config["maps"].keys())}')

        start_time = time.time_ns()
        logger.debug(f"get_values: {map_name} {key}")
    
        if _map["dtypes"][0] == 'h':
            if isinstance(key, str):
                _hex = key
                key = bytes.fromhex(key)
            else:
                _hex = bytes(key).hex()
        else:
            assert isinstance(key, str), "key must be a string for non-hash keys"
            _hex = hex(fnvhash(key.encode('utf-8')))[2:]
            key = key.encode('utf-8')

        logger.debug(f"hash: {(time.time_ns() - start_time) / 1e6:.2f}ms")
        start_time = time.time_ns()
        
        decode_dtype = _map["dtypes"][1]

        if "larges" in _map and _hex in _map["larges"]:
            _bytes = read_large(_map["larges"][_hex], _map["dtypes"][1])
            logger.debug(f"read large: {(time.time_ns() - start_time) / 1e6:.2f}ms")
            start_time = time.time_ns()

            # compress string data is not compressed in larges
            if decode_dtype == 'cs':
                decode_dtype = 's'
        else:
            # use fnv hash as shading idx if key is not a git sha
            _bytes = get_from_tch(key, _map["shards"], _map["sharding_bits"], _map["dtypes"][0] != 'h')
            logger.debug(f"get from tch: {(time.time_ns() - start_time) / 1e6:.2f}ms")
            start_time = time.time_ns()

        _ret = decode_value(_bytes, decode_dtype)
        logger.debug(f"decode value: {len(_ret)}items {(time.time_ns() - start_time) / 1e6:.2f}ms")
        return _ret

    def get_pos(
        self,
        obj: str,
        key: bytes,
    ) -> Tuple[int, int]:
        """
        Get offset and length of a stacked binary object, currently only support blob.
        Move out this part because it's much cheaper than measuring the whole object.
        """
        if obj == 'blob':
            _map_obj = self.config['objects']['sha1.blob.tch']
            v = get_from_tch(key, 
                shards=_map_obj['shards'],
                sharding_bits=_map_obj['sharding_bits'],
                use_fnv_keys=False
            )
            return unber(v)
        else:
            raise ValueError(f'Unsupported object type: {obj}, expected blob')

    def show_content(
        self,
        obj: str,
        key: Union[bytes, str],
    ):
        """Eqivalent to showCnt in WoC perl API
        >>> show_content('tree', '7a374e58c5b9dec5f7508391246c48b73c40d200')  # doctest: +SKIP
        ...
        """
        start_time = time.time_ns()
        logger.debug(f"show_content: {obj} {key}")


        if isinstance(key, str):
            key = bytes.fromhex(key)

        logger.debug(f"hash: {(time.time_ns() - start_time) / 1e6:.2f}ms")
        start_time = time.time_ns()

        if obj == 'tree':
            _map_obj = self.config['objects']['tree.tch']
            v = get_from_tch(key, 
                shards=_map_obj['shards'],
                sharding_bits=_map_obj['sharding_bits'],
                use_fnv_keys=False
            )
            logger.debug(f"get from tch: {(time.time_ns() - start_time) / 1e6:.2f}ms")
            start_time = time.time_ns()
            _ret = decode_tree(decomp_or_raw(v))
            logger.debug(f"decode tree: {len(_ret)}items {(time.time_ns() - start_time) / 1e6:.2f}ms")
            return _ret

        elif obj == 'commit':
            _map_obj = self.config['objects']['commit.tch']
            v = get_from_tch(key, 
                shards=_map_obj['shards'],
                sharding_bits=_map_obj['sharding_bits'],
                use_fnv_keys=False
            )
            logger.debug(f"get from tch: {(time.time_ns() - start_time) / 1e6:.2f}ms")
            return decode_str(decomp_or_raw(v))

            # # Don't decode commit here to be compatible with Perl API
            # _ret = decode_commit(decomp_or_raw(v))
            # logger.debug(f"decode commit: {len(_ret)}items {(time.time_ns() - start_time) / 1e6:.2f}ms")
            # return _ret

        elif obj == 'blob':
            offset, length = self.get_pos('blob', key)
            logger.debug(f"get from tch: offset={offset} len={length} {(time.time_ns() - start_time) / 1e6:.2f}ms")
            start_time = time.time_ns()

            _map_obj = self.config['objects']['blob.bin']
            shard = get_shard(key, _map_obj['sharding_bits'], use_fnv_keys=False)

            with open(_map_obj['shards'][shard], "rb") as f:
                f.seek(offset)
                _out_bin = f.read(length)
            logger.debug(f"read blob: {(time.time_ns() - start_time) / 1e6:.2f}ms")
            start_time = time.time_ns()

            _ret = decode_str(decomp_or_raw(_out_bin))
            logger.debug(f"decode blob: len={len(_ret)} {(time.time_ns() - start_time) / 1e6:.2f}ms")
            return _ret

        elif obj == 'tkns':
            raise NotImplemented
        elif obj == 'tag':
            raise NotImplemented
        elif obj == 'bdiff':
            raise NotImplemented
        else:
            raise ValueError(f'Unsupported object type: {obj}, expected one of tree, blob, commit, tkns, tag, bdiff')