import re
from typing import Union, Optional, List, Tuple, Set, Generator
from functools import cached_property, lru_cache
from datetime import datetime, timezone, timedelta

from .base import WocMapsBase
from .local import fnvhash

_global_woc: Optional[WocMapsBase] = None

def init_woc(woc: WocMapsBase):
    global _global_woc
    _global_woc = woc

@lru_cache(maxsize=None)
def parse_timezone_offset(offset_str):
    """
    Parse a timezone offset string in the format '+HHMM' or '-HHMM' into a timezone object.
    """
    match = re.match(r'([+-])(\d{2})(\d{2})', offset_str)
    if not match:
        raise ValueError(f"Invalid timezone offset format: {offset_str}")
    sign, hours, minutes = match.groups()
    hours, minutes = int(hours), int(minutes)
    offset = timedelta(hours=hours, minutes=minutes)
    
    if sign == '-':
        offset = -offset
    
    return timezone(offset)
    

class _WocObject:
    woc: WocMapsBase  # WocMap instance
    key: str # Key of the object
    
    def __init__(
        self, 
        *args,
        woc: Optional[WocMapsBase] = None,
        **kwargs,
    ):
        self.woc = woc or _global_woc
        assert self.woc is not None, "WocMaps not initialized: call init_woc() or supply a woc argument"
        
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key})"
    
    def __str__(self) -> str:
        return self.key
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.key == value.key
    
    def hash(self) -> str:
        return hex(hash(self))[2:]
    
    def get_list_values(self, map_name: str):
        try:
            return self.woc.get_values(map_name, self.key)
        except KeyError:
            return []
        
        
class _GitObject(_WocObject):
    """ Base class for SHA1-indexed Git objects (commit, tree, blob) """
    def __init__(
        self,
        key: str,
        *args,
        woc: Optional[WocMapsBase] = None,
        **kwargs,
    ):
        super().__init__(*args, woc=woc, **kwargs)
        assert len(key) == 40, "SHA1 hash must be 40 characters long"
        self.key = key
        
    @cached_property
    def data(self):
        obj = self.__class__.__name__.lower()
        return self.woc.show_content(obj, self.key)
    
    def __hash__(self):
        return int(self.key, 16)
    
    def hash(self) -> str:
        return self.key


class _NamedObject(_WocObject):
    """ Base class for objects indexed by a string key"""
    def __init__(
        self,
        key: str,
        *args,
        woc: Optional[WocMapsBase] = None,
        **kwargs,
    ):
        super().__init__(*args, woc=woc, **kwargs)
        self.key = key
        
    def __hash__(self):
        return fnvhash(self.key.encode())
        
        
class Author(_NamedObject):
    @cached_property
    def _username_email(self) -> Tuple[str, str]:
        _splited = self.key.split(' <', 1)
        if len(_splited) == 1:
            return _splited[0], ''
        return _splited[0], _splited[1][:-1]
        
    @property
    def name(self) -> str:
        return self._username_email[0]
    
    @property
    def email(self) -> str:
        return self._username_email[1]
    
    @cached_property
    def blobs(self) -> 'List[Blob]':
        return [Blob(b) for b in self.get_list_values('a2b')]
    
    @cached_property
    def commits(self) -> 'List[Commit]':
        return [Commit(c) for c in self.get_list_values('a2c')]
    
    @cached_property
    def files(self) -> 'List[File]':
        return [File(f) for f in self.get_list_values('a2f')]
    
    @cached_property
    def projects(self) -> 'List[Project]':
        return [Project(p) for p in self.get_list_values('a2p')]


class UniqueAuthor(Author):
    pass


class Blob(_GitObject):
    @cached_property
    def _pos(self) -> Tuple[int, int]:
        return self.woc.get_pos('blob', self.key)
    
    def __len__(self) -> int:
        return self._pos[1]
    
    @cached_property
    def commits(self) -> 'List[Commit]':
        return [Commit(sha) for sha in self.get_list_values('b2c')]
    
    @cached_property
    def first_author(self) -> 'Tuple[datetime, Author, Commit]':
        """ 
        Returns the timestamp, author, and commit of the first author.
        >>> woc.get_values('b2fa', '05fe634ca4c8386349ac519f899145c75fff4169'))
        (datetime.datetime(2014, 9, 7, 2, 59, 48), Author(Audris Mockus <audris@utk.edu>), Commit(e4af89166a17785c1d741b8b1d5775f3223f510f))
        """
        _out = self.woc.get_values('b2fa', self.key)
        _date = datetime.fromtimestamp(int(_out[0]))
        _author = Author(_out[1])
        _commit = Commit(_out[2])
        return _date, _author, _commit
    
    @cached_property
    def time_author_commits(self) -> 'List[Tuple[datetime, Author, Commit]]':
        _out = self.get_list_values('b2tac')
        return [(datetime.fromtimestamp(int(d[0])), Author(d[1]), Commit(d[2])) for d in _out]
    
    @cached_property
    def files(self) -> 'List[File]':
        return [File(f) for f in self.get_list_values('b2f')]
    
    @cached_property
    def projects_unique(self) -> 'List[UpstreamProject]':
        return [UpstreamProject(p) for p in self.get_list_values('b2P')]


class Commit(_GitObject):
    @cached_property
    def data_obj(self):
        _ret = {}
        (_ret['tree'],
            _ret['parent'],
            (_ret['author'], _ret['author_timestamp'], _ret['author_timezone']),
            (_ret['committer'], _ret['committer_timestamp'], _ret['committer_timezone']),
            _ret['message'],
        ) = self.data
        return _ret
    
    @property
    def author(self) -> Author:
        return Author(self.data_obj['author'])
    
    @property
    def authored_at(self) -> datetime:
        tz = parse_timezone_offset(self.data_obj['author_timezone'])
        return datetime.fromtimestamp(int(self.data_obj['author_timestamp']), tz)
    
    @property
    def committer(self) -> Author:
        return Author(self.data_obj['committer'])
    
    @property
    def committed_at(self) -> datetime:
        tz = parse_timezone_offset(self.data_obj['committer_timezone'])
        return datetime.fromtimestamp(int(self.data_obj['committer_timestamp']), tz)
    
    @property
    def full_message(self) -> str:
        """Full message of the commit"""
        return self.data_obj['message']
    
    @property
    def message(self) -> str:
        """Short message of the commit"""
        return self.data_obj['message'].split('\n', 1)[0]
    
    @cached_property
    def tree(self) -> 'Tree':
        return Tree(self.data_obj['tree'])
    
    @property
    def parents(self) -> List['Commit']:
        return [Commit(p) for p in self.data_obj['parent']]
    
    @cached_property
    def projects(self) -> List['Project']:
        """Projects associated with this commit"""
        return [Project(p) for p in self.get_list_values('c2p')]
    
    @cached_property
    def children(self) -> List['Commit']:
        """Children of this commit"""
        return [Commit(c) for c in self.get_list_values('c2cc')]
    
    @cached_property
    def files(self) -> List['File']:
        """Files changed in this commit"""
        return [File(f) for f in self.get_list_values('c2f')]
    
    @cached_property
    def blobs(self) -> List['Blob']:
        """Blobs changed in this commit"""
        return [Blob(b) for b in self.get_list_values('c2b')]
    
    @cached_property
    def time_author(self) -> Tuple[datetime, Author]:
        """Timestamp and author of the commit"""
        res = self.woc.get_values('c2ta', self.key)
        return datetime.fromtimestamp(int(res[0])), Author(res[1])
    
    @cached_property
    def root(self) -> 'Tuple[Commit, int]':
        """Root commit of the project"""
        sha, dis = self.woc.get_values('c2r', self.key)
        return Commit(sha), int(dis)
        

class File(_NamedObject):
    @property
    def path(self) -> str:
        return self.key
    
    @property
    def name(self) -> str:
        return self.key.split('/')[-1]
    
    @cached_property
    def authors(self) -> List[Author]:
        return [Author(a) for a in self.get_list_values('f2a')]
    
    @cached_property
    def blobs(self) -> List[Blob]:
        return [Blob(b) for b in self.get_list_values('f2b')]
    
    @cached_property
    def commits(self) -> List[Commit]:
        return [Commit(c) for c in self.get_list_values('f2c')]
        
        
class Tree(_GitObject):
    @cached_property
    def data(self) -> str:
        return self.woc.show_content('tree', self.key)
    
    @cached_property
    def _file_names(self) -> Set[str]:
        return set(l[1] for l in self.data)
    
    @cached_property
    def _blob_shas(self) -> Set[str]:
        return set(l[2] for l in self.data)
    
    @property
    def files(self) -> str:
        return [File(f) for f in self._file_names]
    
    @property
    def blobs(self) -> str:
        return [Blob(b) for b in self._blob_shas]
    
    def traverse(self) -> 'Generator[Tuple[File, Blob], None, None]':
        for mode, fname, sha in self.data:
            # trees are always 40000:
            # https://stackoverflow.com/questions/1071241
            if mode != '40000':
                yield File(fname), Blob(sha)
            else:
                for _mode, _fname, _sha in Tree(sha).traverse():
                    yield File(fname + '/' + _fname), Blob(_sha)
    
    def __contains__(self, item: Union[str, File, Blob]) -> bool:
        if isinstance(item, str):
            return item in self._file_names or item in self._blob_shas
        if isinstance(item, File):
            return item.text in self._file_names
        if isinstance(item, Blob):
            return item.hex in self._blob_shas
        return False
    
    def __str__(self) -> str:
        return '\n'.join([''.join(l) for l in self.data])
    
    def __len__(self) -> int:
        return len(self.data)


class Project(_NamedObject):
    @property
    def platform(self) -> str:
        raise NotImplemented
    
    @property
    def url(self) -> str:
        raise NotImplemented
    
    @cached_property
    def authors(self) -> 'List[Author]':
        return [Author(a) for a in self.get_list_values('p2a')]
    
    @cached_property
    def commits(self) -> 'List[Commit]':
        return [Commit(c) for c in self.get_list_values('p2c')]
    
    @cached_property
    def upstream_projects(self) -> 'List[UpstreamProject]':
        return [UpstreamProject(p) for p in self.get_list_values('p2P')]
    
    
class UpstreamProject(Project):
    @cached_property
    def unique_authors(self) -> 'List[Author]':
        return [UniqueAuthor(a) for a in self.get_list_values('P2A')]
    
    @cached_property
    def commits(self) -> 'List[Commit]':
        return [Commit(c) for c in self.get_list_values('P2c')]
    
    @cached_property
    def projects(self) -> 'List[Project]':
        return [Project(p) for p in self.get_list_values('P2p')]