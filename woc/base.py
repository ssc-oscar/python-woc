from typing import Union, Literal, List, Tuple, Dict

WocObjectsWithContent = Literal['tree', 'blob', 'commit', 'tkns', 'tag', 'bdiff']
WocSupportedProfileVersions = (1, )


class WocMapsBase:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("WocMapsBase is an abstract class, use WoCMapsLocal instead")
    
    def get_values(
        self,
        map_name: str,
        key: Union[bytes, str],
    ) -> Union[List[str], Tuple[str, str, str], List[Tuple[str, str, str]]]:
        """Eqivalent to getValues in WoC Perl API
        >>> self.get_values('P2c', 'user2589_minicms')
        ['05cf84081b63cda822ee407e688269b494a642de', ...]
        >>> self.get_values('c2r', 'e4af89166a17785c1d741b8b1d5775f3223f510f')
        ('9531fc286ef1f4753ca4be9a3bf76274b929cdeb', 27)
        >>> self.get_values('b2fa', '05fe634ca4c8386349ac519f899145c75fff4169')
        ('1410029988',
         'Audris Mockus <audris@utk.edu>',
         'e4af89166a17785c1d741b8b1d5775f3223f510f')
        """
        raise NotImplementedError("WocMapsBase is an abstract class, use WoCMapsLocal instead")

    def show_content(
        self,
        obj_name: WocObjectsWithContent,
        key: Union[bytes, str],
    ) -> Union[List[Tuple[str, str, str]], str, Tuple[str, Tuple[str, str, str], Tuple[str, str, str], str]]:
        """
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
        raise NotImplementedError("WocMapsBase is an abstract class, use WoCMapsLocal instead")
                 