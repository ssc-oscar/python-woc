from typing import Iterable, Union, Tuple, List

from .base import WocMapsBase, WocObjectsWithContent

class WocMapsLocal(WocMapsBase):
    def __init__(self, 
            profile_path: str | Iterable[str] | None = None,
            version: str | Iterable[str] | None = None
        ) -> None: 
        ...

    def get_values(
        self,
        map_name: str,
        key: Union[bytes, str],
    ) -> (list[str] | tuple[str, str, str] | list[tuple[str, str, str]]):
        ...

    def show_content(
        self,
        obj: WocObjectsWithContent,
        key: Union[bytes, str],
    ) -> (list[tuple[str, str, str]] | str):
        ...

# Make utility functions accessible from Python -> easier testing
def fnvhash(data: bytes) -> int: ...
def unber(buf: bytes) -> bytes: ...
def lzf_length(raw_data: bytes) -> Tuple[int, int]: ...
def get_tch(path: str): ...
def get_shard(key: bytes, sharding_bits: int, use_fnv_keys: bool) -> int: ...
def get_from_tch(key: bytes, shards: List[bytes], sharding_bits: int, use_fnv_keys: bool) -> bytes: ...