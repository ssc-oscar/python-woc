import gzip
import json
from typing import List, Union

try:
    import lzf

    assert lzf.decompress
except ImportError or AssertionError:
    raise ImportError(
        "python-lzf is required to decompress LZF-compressed data: `pip install python-lzf`"
    )

from woc.local import *
from woc.tch import TCHashDB


def ber(*numbers):
    def gen():
        for num in numbers:
            a = True
            while a:
                a, num = divmod(num, 128)
                yield (a + 0x80 if a else num).to_bytes(1, "big")

    return b"".join(gen())


def encode_value(value, dtype: str) -> bytes:
    if dtype == "h":  # type: list[str]
        return b"".join(bytes.fromhex(v) for v in value)
    elif dtype == "sh":  # type: tuple[str, str, str]
        Time, Author, cmt_sha = value
        buf0 = f"{Time};{Author}".encode()
        cmt_sha_bytes = bytes.fromhex(cmt_sha)
        return buf0 + cmt_sha_bytes
    elif dtype == "cs3":  # type: list[tuple[str, str, str]]
        _joined = ";".join(f"{t[0]};{t[1]};{t[2]}" for t in value)
        data = _joined.encode
        return lzf.compress(data)
    elif dtype == "cs":  # type: list[str]
        _joined = ";".join(v.encode() for v in value if v)
        return lzf.compress(_joined.encode())
    elif dtype == "s":  # type: list[str]
        return b";".join(v.encode() for v in value)
    elif dtype == "r":  # type: list[str, int]
        _hex, _len = value
        return bytes.fromhex(_hex) + ber(_len)
    elif dtype == "hhwww":
        raise NotImplementedError
    raise ValueError(f"Unsupported dtype: {dtype}")


def write_to_tch(
    key: bytes, value: bytes, shards: List[str], sharding_bits: int, use_fnv_keys: bool
):
    shard = get_shard(key, sharding_bits, use_fnv_keys)
    _path = shards[shard]
    db = TCHashDB(_path)
    db[key] = value
    db.close()


def write_large(path: str, key: bytes, value: bytes, dtype: str):
    if dtype == "h":
        with open(path, "wb") as f:
            f.write(key)
            f.write(value[:160])
    else:
        # use zlib to decompress
        with gzip.open(path, "wb") as f:
            f.write(key)
            f.write(b"\n")
            # run a fast scan to find idx of 3rd ';' in value
            idx = 0
            for _ in range(3):
                idx = value.find(b";", idx + 1)
            f.write(value[:idx])


class WocMapsCopier(WocMapsLocal):
    def __init__(self, config1, config2):
        super().__init__(config1)
        with open(config2) as f:
            self.config2 = json.load(f)

    def copy_values(self, map_name, key):
        """One large file can only contain one record"""
        try:
            value, _, _ = self._get_tch_bytes(map_name, key)
        except ValueError:
            print(self._get_tch_bytes(map_name, key))
            raise

        if map_name in self.config2["maps"]:
            _map = self.config2["maps"][map_name][0]
        elif map_name in self.config2["objects"]:
            _map = self.config2["objects"][map_name]
        else:
            raise KeyError(
                f'Invalid map name: {map_name}, '
                f'expect one of {", ".join(self.config2["maps"].keys())}'
            )

        if _map["dtypes"][0] == "h":
            if isinstance(key, str):
                _hex = key
                key = bytes.fromhex(key)
            else:
                _hex = bytes(key).hex()
        else:
            assert isinstance(key, str), "key must be a string for non-hash keys"
            _hex = hex(fnvhash(key.encode("utf-8")))[2:]
            key = key.encode("utf-8")

        if "larges" in _map and _hex in _map["larges"]:
            print(
                "writing large",
                _map["larges"][_hex],
                "key",
                key,
                "dtype",
                _map["dtypes"][1],
            )
            return write_large(_map["larges"][_hex], key, value, _map["dtypes"][1])
        else:
            # use fnv hash as shading idx if key is not a git sha
            print("writing to tch", key, _map["sharding_bits"], _map["dtypes"][0] != "h")
            return write_to_tch(
                key,
                value,
                _map["shards"],
                _map["sharding_bits"],
                _map["dtypes"][0] != "h",
            )

    def copy_content(self, obj: str, key: Union[bytes, str]):
        """One blob shard can only contain one record"""
        value, _, _ = self._get_tch_bytes(obj, key)

        if obj in ("tree", "commit", "tag"):
            _map_obj = self.config2["objects"][f"{obj}.tch"]
            print("writing to tch", key, _map_obj["sharding_bits"])
            write_to_tch(
                bytes.fromhex(key),
                value,
                _map_obj["shards"],
                _map_obj["sharding_bits"],
                use_fnv_keys=False,
            )

        elif obj == "blob":
            # read blob
            key = bytes.fromhex(key) if isinstance(key, str) else key
            offset, length = self._get_pos("blob", key)
            _map_obj = self.config["objects"]["blob.bin"]
            shard = get_shard(key, _map_obj["sharding_bits"], use_fnv_keys=False)
            _p = _map_obj["shards"][shard]
            if isinstance(_p, dict):
                _p = _p["path"]
            with open(_p, "rb") as f:
                f.seek(offset)
                _v = f.read(length)
            # write tch
            _map_obj = self.config2["objects"]["sha1.blob.tch"]
            _idx = ber(0, length)
            print("writing to tch", key, _map_obj["sharding_bits"])
            write_to_tch(
                key,
                _idx,
                _map_obj["shards"],
                _map_obj["sharding_bits"],
                use_fnv_keys=False,
            )
            # write blob
            _map_obj = self.config2["objects"]["blob.bin"]
            shard = get_shard(key, _map_obj["sharding_bits"], use_fnv_keys=False)
            print("writing to file", _map_obj["shards"][shard], length)
            with open(_map_obj["shards"][shard], "ab") as f:
                f.write(_v)

        else:
            raise ValueError(
                f"Unsupported object type: {obj}, expected one of tree, blob, commit"
            )


if __name__ == "__main__":
    import glob
    import os

    for f in glob.glob("./tests/fixtures/*.tch*") + glob.glob("./tests/fixtures/*.bin"):
        print("removing", f)
        os.remove(f)

    cp = WocMapsCopier("./wocprofile.json", "./tests/test_profile.json")
    cp.copy_values("c2p", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    cp.copy_values("c2dat", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    cp.copy_values("c2ta", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    cp.copy_values("b2tac", "05fe634ca4c8386349ac519f899145c75fff4169")
    cp.copy_values("p2a", "ArtiiQ_PocketMine-MP")
    cp.copy_values("b2c", "05fe634ca4c8386349ac519f899145c75fff4169")
    cp.copy_values("b2c", "3f2eca18f1bc0f3117748e2cea9251e5182db2f7")  # large
    cp.copy_values("a2c", "Audris Mockus <audris@utk.edu>")
    # cp.copy_values('c2cc', 'e4af89166a17785c1d741b8b1d5775f3223f510f') # null
    cp.copy_values("a2f", "Audris Mockus <audris@utk.edu>")
    cp.copy_values("c2f", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    # cp.copy_values("c2b", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    cp.copy_values("p2c", "ArtiiQ_PocketMine-MP")
    cp.copy_values("f2a", "youtube-statistics-analysis.pdf")
    cp.copy_values("b2f", "05fe634ca4c8386349ac519f899145c75fff4169")
    cp.copy_values("c2r", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    cp.copy_values("b2fa", "05fe634ca4c8386349ac519f899145c75fff4169")
    cp.copy_content("tree", "f1b66dcca490b5c4455af319bc961a34f69c72c2")
    cp.copy_content("commit", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    cp.copy_content("blob", "05fe634ca4c8386349ac519f899145c75fff4169")
    cp.copy_content("blob", "46aaf071f1b859c5bf452733c2583c70d92cd0c8")
    # woc-hack_thebridge
    cp.copy_values("p2c", "woc-hack_thebridge")
    cp.copy_content("commit", "0d8228bb25ce89c7e731c7410bc8c5a4e2636e52")
    cp.copy_content("commit", "34a8662a4f31dacb923e39ae6792f6fc4476a939")
    cp.copy_content("commit", "898d5a21241aaf16acf92566aa34103d06cf2ac6")
    cp.copy_content("commit", "91f4da4c173e41ffbf0d9ecbe2f07f3a3296933c")
    cp.copy_content("commit", "ae6e15fa4d8d4d454977ddbb4e97e922ddecebf7")
    cp.copy_content("commit", "f249b14a111279faa8d65c29ecf46bb6ce59a139")
    cp.copy_content("tree", "706aa4dedb560358bff21c3120a0b09532d3484d")
    cp.copy_content("tree", "3ccf6f8320740a1afec68b38b3b9ba46cedef368")
    cp.copy_content("tree", "e5798457aebae7c84eff7b80b50c3a938cc4cb63")
    cp.copy_content("tree", "836f04d5b374033b1608269e2f3aaabae263a0db")
    cp.copy_content("tree", "f54cb5527226aa2096307c08e15c62248b98f763")
    cp.copy_content("tree", "da65e1401d11a955686b8a49e46b9a457f3febab")
    cp.copy_content("tree", "a28f1558be9867d35cc1fa17477565c08786cf83")
    cp.copy_content("tree", "4db2ad30097924cbe5da9c0f2c49350fdc19c3a4")
    cp.copy_content("tree", "1cf86145b4a9492ebbe0fa640638504946315ca6")
    cp.copy_content("tree", "29a422c19251aeaeb907175e9b3219a9bed6c616")
    cp.copy_content("tree", "51968a7a4e67fd2696ffd5ccc041560a4d804f5d")
    # copy tag
    cp.copy_content("tag", "08af22b7de836a5fef0f9947a5f0894d371742de")
    cp.copy_content("tag", "8878cb40eaac07818e1e6c8d5e4b21660c9a8432")
    cp.copy_values("c2tag", "fcadcb9366d4a011039e384affa10961e99cf2c4")
