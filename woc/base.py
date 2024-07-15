from dataclasses import dataclass
from typing import Dict, List, Literal, Optional, Tuple, Union

WocObjectsWithContent = Literal["tree", "blob", "commit", "tkns", "tag", "bdiff"]
"""WoC objects stored in stacked binary files."""

WocSupportedProfileVersions = (1, 2)
"""Profile versions supported by the current python-woc."""


@dataclass
class WocFile:
    """Represents a file in the WoC database."""

    path: str
    """Path to the file in the local filesystem."""

    size: Optional[int] = None
    """Size of file in bytes."""

    digest: Optional[str] = None
    """16-char digest calculated by woc.utils.fast_digest."""


@dataclass
class WocObject:
    name: str
    """Name of the map, e.g. 'c2p', 'c2r', 'P2c'."""

    sharding_bits: int
    """Number of bits used for sharding."""

    shards: List[WocFile]
    """List of shard files."""


@dataclass
class WocMap(WocObject):
    version: str
    """version of the map, e.g. 'R', 'U'."""

    larges: Dict[str, WocFile]
    """Large files associated with the map."""

    dtypes: Tuple[str, str]
    """Data types of the map, e.g. ('h', 'cs'), ('h', 'hhwww')."""


class WocMapsBase:
    maps: List[WocMap]
    """List of basemaps available in the WoC database."""
    objects: List[WocObject]
    """List of objects available in the WoC database."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "WocMapsBase is an abstract class, use WoCMapsLocal instead"
        )

    def get_values(
        self,
        map_name: str,
        key: Union[bytes, str],
    ) -> Union[List[str], Tuple[str, str, str], List[Tuple[str, str, str]]]:
        """
        Eqivalent to getValues in WoC Perl API.

        :param map_name: The name of the map, e.g. 'c2p', 'c2r', 'P2c'
        :param key: The key of the object. For git objects, it is the SHA-1 hash of the object
                    (in bytes or hex string). For other objects like Author, it is the name of the object.
        :return: The value of the object. Can be a list of strings, a tuple of strings, or a list of tuples of strings. Please refer to the documentation for details.

        >>> self.get_values('P2c', 'user2589_minicms')
        ['05cf84081b63cda822ee407e688269b494a642de', ...]
        >>> self.get_values('c2r', 'e4af89166a17785c1d741b8b1d5775f3223f510f')
        ('9531fc286ef1f4753ca4be9a3bf76274b929cdeb', 27)
        >>> self.get_values('b2fa', '05fe634ca4c8386349ac519f899145c75fff4169')
        ('1410029988',
         'Audris Mockus <audris@utk.edu>',
         'e4af89166a17785c1d741b8b1d5775f3223f510f')
        """
        raise NotImplementedError("WocMapsBase is an abstract class")

    def show_content(
        self,
        obj_name: WocObjectsWithContent,
        key: Union[bytes, str],
    ) -> Union[
        List[Tuple[str, str, str]],
        str,
        Tuple[str, Tuple[str, str, str], Tuple[str, str, str], str],
    ]:
        """
        Eqivalent to showCnt in WoC Perl API.

        :param obj_name: The name of the object, e.g. 'blob', 'tree', 'commit'
        :param key: The key of the object. It is the SHA-1 hash of the object (in bytes or hex string).
        :return: The content of the object. Can be a list of tuples of strings, a string, or a tuple of strings.

        >>> self.show_content('blob', '05fe634ca4c8386349ac519f899145c75fff4169')
        'This is the content of the blob'
        Eqivalent to showCnt in WoC perl API
        >>> self.show_content('tree', '7a374e58c5b9dec5f7508391246c48b73c40d200')
        [('100644', '.gitignore', '8e9e1...'), ...]
        >>> self.show_content('commit', 'e4af89166a17785c1d741b8b1d5775f3223f510f')
        ('f1b66dcca490b5c4455af319bc961a34f69c72c2',
         ('c19ff598808b181f1ab2383ff0214520cb3ec659',),
         ('Audris Mockus <audris@utk.edu> 1410029988', '1410029988', '-0400'),
         ('Audris Mockus <audris@utk.edu>', '1410029988', '-0400'),
        'News for Sep 5, 2014\\n')
        """
        raise NotImplementedError("WocMapsBase is an abstract class")

    def count(self, map_name: str) -> int:
        """
        Count the number of keys in a map.

        :param map_name: The name of the mapping / object, e.g. 'c2p', 'c2r', 'commit'.
        :return: The number of keys in the tch databases plus the number of large files.

        >>> self.count('c2r')
        12345
        """
        raise NotImplementedError("WocMapsBase is an abstract class")
