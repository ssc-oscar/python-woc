import os
from typing import Tuple, Union, Literal

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
    

class WocKeyError(KeyError):
    def __init__(self, 
        key: bytes,
        file_path: str,
    ) -> None:
        try:
            _decoded_key = key.decode('utf-8')
        except UnicodeDecodeError:
            _decoded_key = key.hex()
        _filename = os.path.basename(file_path)
        self.message = f"{_decoded_key} in {_filename}"
        super().__init__(self.message)

        
                 