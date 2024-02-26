# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False, profile=True
# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-01-17

import os
import json
from libc.stdint cimport uint8_t, uint16_t, uint32_t, uint64_t
from typing import Tuple, Dict, Iterable, List, Union, Literal
import zlib

try:
    import lzf
    assert lzf.decompress
except ImportError or AssertionError:
    raise ImportError('python-lzf is required to decompress LZF-compressed data: `pip install python-lzf`')

from .base import WocMapsBase, WocKeyError, WocObjectsWithContent, WocSupportedProfileVersions
from .tch cimport fnvhash, get_from_tch, get_shard

cdef unber(bytes buf):
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

cdef (int, int) lzf_length(bytes raw_data):
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


class WocMapsLocal(WocMapsBase):
    def __init__(self, 
            profile_path: str | Iterable[str] | None = None,
            version: str | Iterable[str] | None = None
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
                                    "run `python3 -m woc detect` to generate".format(profile_path))

        # check profile
        assert self.config["wocSchemaVersion"] in WocSupportedProfileVersions, \
                                    "Unsupported wocprofile version: {}".format(self.config["wocSchemaVersion"])
        assert self.config["maps"], "Run `python3 -m woc detect` to scan data files and generate wocprofile.json"

    @staticmethod
    def _read_large(path: str, dtype: str) -> bytes:
        """Read a *.large.* and return its content""" 
        if dtype == 'h':
            with open(path, 'rb') as f:
                f.seek(20) # 160 bits of SHA1
                return f.read()
        else:
            # use zlib to decompress
            with open(path, 'rb') as f:
                _uncompressed = zlib.decompress(f.read())
                # find first 256 bytes for b'\n', don't scan the whole document
                _idx = _uncompressed[:256].find(b'\n')
                if _idx > 0:
                    return _uncompressed[_idx+1:]  # a2f
                return _uncompressed  # b2tac

    def _decode_value(
        self,
        value: bytes,
        out_dtype: str
    ):
        if out_dtype == 'h':  # type: list[str]
            return [value[i:i + 20].hex() for i in range(0, len(value), 20)]
        elif out_dtype == 'sh':  # type: tuple[str, str, str]
            buf0 = value[0:len(value)-21]
            cmt_sha = value[(len(value)-20):len(value)]
            (Time, Author) = buf0.decode('utf-8').split(";")
            return (Time, Author, cmt_sha.hex())  
        elif out_dtype == 'cs3':  # type: list[tuple[str, str, str]]
            data = decomp(value)
            _splited = data.decode('utf-8').split(";")
            return [
                (_splited[i],_splited[i+1],_splited[i+2])
                for i in range(0, len(_splited), 3)
            ] 
        elif out_dtype == 'cs':   # type: list[str]
            data = decomp(value)
            return [v.decode('utf-8')
                for v in data.split(b';')
                if v and v != b'EMPTY'] 
        elif out_dtype == 's':  # type: list[str]
            return value.decode('utf-8').split(';')
        elif out_dtype == 'r':  # type: list[str, int]
            _hex = value[:20].hex()
            _len = unber(value[20:])[0]
            return (_hex, _len)
        elif out_dtype == 'hhwww':
            raise NotImplemented
        raise ValueError(f'Unsupported dtype: {out_dtype}')

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
    
        if _map["dtypes"][0] == 'h':
            if isinstance(key, str):
                _hex = key
                key = bytes.fromhex(key)
            else:
                _hex = bytes.hex(key)
        else:
            assert isinstance(key, str), "key must be a string for non-hash keys"
            _hex = bytes(fnvhash(key.encode('utf-8'))).hex()
            key = key.encode('utf-8')

        if "larges" in _map and _hex in _map["larges"]:
            _bytes = self._read_large(_map["larges"][_hex], _map["dtypes"][0])
        else:
            # use fnv hash as shading idx if key is not a git sha
            _bytes = get_from_tch(key, _map["shards"], _map["sharding_bits"], _map["dtypes"][0] != 'h')

        return self._decode_value(_bytes, _map["dtypes"][1])

    @staticmethod
    def _decode_tree(
        value: bytes
    ) -> list[tuple[str, str, str]]:
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
                _file_buf.append(_curr_buf.decode('utf-8'))
                _curr_buf = bytes()
            elif value[i] == 0x00:
                _file_buf.append(_curr_buf.decode('utf-8'))
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

    @staticmethod
    def _read_file_with_offset(file_path, offset, length):
        with open(file_path, "rb") as f:
            f.seek(offset)
            return f.read(length)

    def show_content(
        self,
        obj: str,
        key: Union[bytes, str],
    ):
        """Eqivalent to showCnt in WoC perl API
        >>> show_content('tree', '7a374e58c5b9dec5f7508391246c48b73c40d200')  # doctest: +SKIP
        ...
        """
        if isinstance(key, str):
            key = bytes.fromhex(key)

        if obj == 'tree':
            _map_obj = self.config['objects']['tree.tch']
            v = get_from_tch(key, 
                shards=_map_obj['shards'],
                sharding_bits=_map_obj['sharding_bits'],
                use_fnv_keys=False
            )
            return self._decode_tree(decomp_or_raw(v))
        elif obj == 'commit':
            _map_obj = self.config['objects']['commit.tch']
            v = get_from_tch(key, 
                shards=_map_obj['shards'],
                sharding_bits=_map_obj['sharding_bits'],
                use_fnv_keys=False
            )
            return decomp_or_raw(v).decode('utf-8')
        elif obj == 'blob':
            _map_obj = self.config['objects']['sha1.blob.tch']
            v = get_from_tch(key, 
                shards=_map_obj['shards'],
                sharding_bits=_map_obj['sharding_bits'],
                use_fnv_keys=False
            )
            offset, length = unber(v)
            _map_obj = self.config['objects']['blob.bin']
            shard = get_shard(key, _map_obj['sharding_bits'], use_fnv_keys=False)
            _out_bin = self._read_file_with_offset(
                _map_obj['shards'][shard],
                offset,
                length
            )
            return decomp_or_raw(_out_bin).decode('utf-8')
        elif obj == 'tkns':
            raise NotImplemented
        elif obj == 'tag':
            raise NotImplemented
        elif obj == 'bdiff':
            raise NotImplemented
        else:
            raise ValueError(f'Unsupported object type: {obj}, expected one of tree, blob, commit, tkns, tag, bdiff')