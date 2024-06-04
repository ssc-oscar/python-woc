from typing import Union, Literal

WocObjectsWithContent = Literal['tree', 'blob', 'commit', 'tkns', 'tag', 'bdiff']
WocSupportedProfileVersions = (1, )


class WocMapsBase:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("WocMapsBase is an abstract class, use WoCMapsLocal instead")

    def get_values(
        self,
        map_name: str,
        key: Union[bytes, str],
    ):
        raise NotImplementedError("WocMapsBase is an abstract class, use WoCMapsLocal instead")

    def show_content(
        self,
        obj: WocObjectsWithContent,
        key: Union[bytes, str],
    ):
        raise NotImplementedError("WocMapsBase is an abstract class, use WoCMapsLocal instead")

        
                 