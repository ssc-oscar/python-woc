from typing import Iterable, Union

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
    ):
        ...

    def show_content(
        self,
        obj: WocObjectsWithContent,
        key: Union[bytes, str],
    ):
        ...