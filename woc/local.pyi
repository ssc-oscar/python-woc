from typing import Iterable, List, Literal, Optional, Tuple, Union

from .base import WocMapsBase

class WocMapsLocal(WocMapsBase):
    def __init__(
        self,
        profile_path: Union[str, Iterable[str], None] = None,
        version: Union[str, Iterable[str], None] = None,
        on_large: Literal["ignore", "head", "all"] = "all",
    ) -> None:
        """
        Initialize local WoC maps with a profile.

        :param profile_path: path to the woc profile.
                             if not provided, use `./wocprofile.json`, `~/.wocprofile.json`, `/home/wocprofile.json`, `/etc/wocprofile.json`.
        :param version: version of the profile, default to the latest version.
                        can be a single version like 'R' or a list of versions like ['R', 'U'].
        :param on_large: how to handle large files, default to 'all' (read all content). 'ignore' to ignore large files, 'head' to read only the first chunk.
        """
        ...

    def _get_tch_bytes(
        self, map_name: str, key: Union[bytes, str]
    ) -> Tuple[bytes, str, Optional[int]]: ...
    def _get_pos(
        self,
        obj_name: str,
        key: Union[bytes, str],
    ) -> Tuple[int, int]:
        """
        Get offset and length of a stacked binary object, currently only support blob.

        Extract this part because it's much cheaper than decode the content.
        >>> self._get_pos('blob', bytes.fromhex('7a374e58c5b9dec5f7508391246c48b73c40d200'))
        (0, 123)
        """
        ...

# The following functions are internal and should not be used by the user
# Exposing them here for testing purposes
def fnvhash(data: bytes) -> int: ...
def unber(buf: bytes) -> bytes: ...
def lzf_length(raw_data: bytes) -> Tuple[int, int]: ...
def decomp(data: bytes) -> bytes: ...
def decomp_or_raw(data: bytes) -> bytes: ...
def get_tch(path: str): ...
def get_shard(key: bytes, sharding_bits: int, use_fnv_keys: bool) -> int: ...

# def get_from_tch(key: bytes, shards: List[bytes], sharding_bits: int, use_fnv_keys: bool) -> bytes: ...
def decode_value(value: bytes, out_dtype: str): ...
def decode_tree(value: bytes) -> List[Tuple[str, str, str]]: ...
def decode_commit(
    commit_bin: bytes,
) -> Tuple[str, Tuple[str, str, str], Tuple[str, str, str], str]: ...
def decode_str(raw_data: str, encoding="utf-8"): ...
