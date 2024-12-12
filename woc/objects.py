import difflib
import re
import os
import warnings
from datetime import datetime, timedelta, timezone
from functools import cached_property, lru_cache
from logging import getLogger
from typing import Dict, Generator, List, Optional, Set, Tuple, Union

from .base import WocMapsBase
from .local import fnvhash

_global_woc: Optional[WocMapsBase] = None
_logger = getLogger(__name__)
_DAY_Z = datetime.fromtimestamp(0, tz=None)


def init_woc_objects(woc: WocMapsBase):
    """
    Stores wocMaps object globally so you don't have to pass it around.

    :param woc: a wocMaps object.
    """
    global _global_woc
    _global_woc = woc


@lru_cache(maxsize=None)
def parse_timezone_offset(offset_str: str) -> timezone:
    """
    Parse a timezone offset string in the format '+HHMM' or '-HHMM' into a timezone object.

    >>> parse_timezone_offset('+0530')
    timezone(timedelta(seconds=19800))
    """
    match = re.match(r"([+-])(\d{2})(\d{2})", offset_str)
    if not match:
        raise ValueError(f"Invalid timezone offset format: {offset_str}")
    sign, hours, minutes = match.groups()
    hours, minutes = int(hours), int(minutes)
    offset = timedelta(hours=hours, minutes=minutes)

    if sign == "-":
        offset = -offset

    return timezone(offset)


class _WocObject:
    _ident: str
    """Identifier of the object"""
    woc: WocMapsBase
    """WocMap instance"""
    key: str
    """Key of the object"""

    def __init__(
        self,
        *args,
        woc: Optional[WocMapsBase] = None,
        **kwargs,
    ):
        self.woc = woc or _global_woc
        assert (
            self.woc is not None
        ), "WocMaps not initialized: call init_woc_objects() or supply a woc keyword argument"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.key})"

    def __str__(self) -> str:
        return self.key

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, self.__class__):
            return False
        return self.key == value.key

    @property
    def hash(self) -> str:
        return hex(hash(self))[2:]

    def _get_list_values(self, map_name: str):
        """A thin wrapper around WocMapsBase.get_values to handle KeyError"""
        try:
            return self.woc.get_values(map_name, self.key)
        except KeyError:
            return []


class _GitObject(_WocObject):
    """Base class for SHA1-indexed Git objects (commit, tree, blob)"""

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

    @property
    def hash(self) -> str:
        return self.key


class _NamedObject(_WocObject):
    """Base class for objects indexed by a string key"""

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
    _ident = "a"

    @cached_property
    def _username_email(self) -> Tuple[str, str]:
        _splited = self.key.split(" <", 1)
        if len(_splited) == 1:
            return _splited[0], ""
        return _splited[0], _splited[1][:-1]

    @property
    def name(self) -> str:
        return self._username_email[0]

    @property
    def email(self) -> str:
        return self._username_email[1]

    @cached_property
    def blobs(self) -> "List[Blob]":
        return [Blob(b) for b in self._get_list_values(f"{self._ident}2b")]

    @cached_property
    def commits(self) -> "List[Commit]":
        return [Commit(c) for c in self._get_list_values(f"{self._ident}2c")]

    @cached_property
    def files(self) -> "List[File]":
        return [File(f) for f in self._get_list_values(f"{self._ident}2f")]

    @cached_property
    def projects(self) -> "List[Project]":
        return [Project(p) for p in self._get_list_values(f"{self._ident}2p")]

    @cached_property
    def unique_authors(self) -> List["UniqueAuthor"]:
        return [UniqueAuthor(a) for a in self._get_list_values(f"{self._ident}2A")]

    @property
    def authors(self):
        raise NotImplementedError("Author object does not have authors method")
    
    @property
    def aliases(self) -> List["Author"]:
        _unique_authors = self.unique_authors
        if len(_unique_authors) == 0:
            return []
        return _unique_authors[0].authors

    @cached_property
    def first_blobs(self) -> List["Blob"]:
        return [Blob(b) for b in self._get_list_values(f"{self._ident}2fb")]


class UniqueAuthor(Author):
    _ident = "A"

    @property
    def unique_authors(self) -> "List[Author]":
        raise NotImplementedError(
            "UniqueAuthor object does not have unique_authors method"
        )

    @cached_property
    def authors(self) -> "List[Author]":
        return [Author(a) for a in self._get_list_values(f"{self._ident}2a")]


class Blob(_GitObject):
    _ident = "b"

    @cached_property
    def _pos(self) -> Tuple[int, int]:
        return self.woc._get_pos("blob", self.key)

    def __len__(self) -> int:
        return self._pos[1]

    def __str__(self) -> str:
        return self.data

    @cached_property
    def commits(self) -> "List[Commit]":
        return [Commit(sha) for sha in self._get_list_values("b2c")]

    @cached_property
    def first_author(self) -> "Tuple[datetime, Author, Commit]":
        """
        Returns the timestamp, author, and commit of the first author.

        >>> woc.get_values('b2fa', '05fe634ca4c8386349ac519f899145c75fff4169'))
        (datetime.datetime(2014, 9, 7, 2, 59, 48), Author(Audris Mockus <audris@utk.edu>), Commit(e4af89166a17785c1d741b8b1d5775f3223f510f))
        """
        _out = self.woc.get_values("b2fa", self.key)
        _date = datetime.fromtimestamp(int(_out[0]))
        _author = Author(_out[1])
        _commit = Commit(_out[2])
        return _date, _author, _commit

    @cached_property
    def time_author_commits(self) -> "List[Tuple[datetime, Author, Commit]]":
        _out = self._get_list_values("b2tac")
        return [
            (datetime.fromtimestamp(int(d[0])), Author(d[1]), Commit(d[2])) for d in _out
        ]

    @cached_property
    def files(self) -> "List[File]":
        return [File(f) for f in self._get_list_values("b2f")]

    @cached_property
    def projects_unique(self) -> "List[RootProject]":
        return [RootProject(p) for p in self._get_list_values("b2P")]

    @cached_property
    def changed_from(self) -> "List[Tuple[Blob, Commit, File]]":
        return [
            (Blob(b), Commit(c), File(f)) for b, c, f in self._get_list_values("bb2cf")
        ]

    @cached_property
    def changed_to(self) -> "List[Tuple[Blob, Commit, File]]":
        return [
            (Blob(b), Commit(c), File(f)) for b, c, f in self._get_list_values("obb2cf")
        ]


class Commit(_GitObject):
    _ident = "c"

    @cached_property
    def data_obj(self):
        _ret = {}
        (
            _ret["tree"],
            _ret["parent"],
            (_ret["author"], _ret["author_timestamp"], _ret["author_timezone"]),
            (_ret["committer"], _ret["committer_timestamp"], _ret["committer_timezone"]),
            _ret["message"],
        ) = self.data
        return _ret

    @property
    def author(self) -> Author:
        return Author(self.data_obj["author"])

    @property
    def authored_at(self) -> datetime:
        tz = parse_timezone_offset(self.data_obj["author_timezone"])
        return datetime.fromtimestamp(int(self.data_obj["author_timestamp"]), tz)

    @property
    def committer(self) -> Author:
        return Author(self.data_obj["committer"])

    @property
    def committed_at(self) -> datetime:
        tz = parse_timezone_offset(self.data_obj["committer_timezone"])
        return datetime.fromtimestamp(int(self.data_obj["committer_timestamp"]), tz)

    @property
    def full_message(self) -> str:
        """Full message of the commit"""
        return self.data_obj["message"]

    @property
    def message(self) -> str:
        """Short message of the commit"""
        return self.data_obj["message"].split("\n", 1)[0]

    @cached_property
    def tree(self) -> "Tree":
        return Tree(self.data_obj["tree"])

    @property
    def _parent_shas(self) -> List[str]:
        return self.data_obj["parent"]

    @property
    def parents(self) -> List["Commit"]:
        """Parent commits of this commit"""
        return [Commit(p) for p in self.data_obj["parent"]]

    @cached_property
    def projects(self) -> List["Project"]:
        """Projects associated with this commit"""
        return [Project(p) for p in self._get_list_values("c2p")]

    @cached_property
    def root_projects(self) -> List["RootProject"]:
        """Root projects associated with this commit"""
        return [RootProject(p) for p in self._get_list_values("c2P")]

    @cached_property
    def children(self) -> List["Commit"]:
        """Children of this commit"""
        return [Commit(c) for c in self._get_list_values("c2cc")]

    @cached_property
    def _file_names(self) -> List[str]:
        return self._get_list_values("c2f")

    @cached_property
    def _file_set(self) -> Set[str]:
        return set(self._file_names)

    @cached_property
    def files(self) -> List["File"]:
        """Files changed in this commit"""
        return [File(f) for f in self._file_names]

    @cached_property
    def _blob_shas(self) -> List[str]:
        return self._get_list_values("c2b")

    @cached_property
    def _blob_set(self) -> Set[str]:
        return set(self._blob_shas)

    @cached_property
    def blobs(self) -> List["Blob"]:
        """
        Blobs changed in this commit.

        This relation is known to miss every first file in all trees.
        Consider using Commit.tree.blobs as a slower but more accurate
        alternative.
        """
        return [Blob(b) for b in self._get_list_values("c2b")]

    @cached_property
    def time_author(self) -> Tuple[datetime, Author]:
        """Timestamp and author of the commit"""
        res = self.woc.get_values("c2ta", self.key)
        return datetime.fromtimestamp(int(res[0])), Author(res[1])

    @cached_property
    def root(self) -> "Tuple[Commit, int]":
        """Root commit of the project"""
        sha, dis = self.woc.get_values("c2r", self.key)
        return Commit(sha), int(dis)

    @cached_property
    def changeset(self) -> "List[Tuple[File, Blob, Blob]]":
        """Returns changed files, their new and old blobs"""
        return [
            (File(f), Blob(new), Blob(old))
            for f, new, old in self._get_list_values("c2fbb")
        ]

    def compare(
        self, parent: Union["Commit", str], threshold=0.5
    ) -> Generator[
        Tuple[Optional["File"], Optional["File"], Optional["Blob"], Optional["Blob"]],
        None,
        None,
    ]:
        """
        Compare two Commits.

        :param parent: another commit to compare to.
                Expected order is `diff = child_commit - parent_commit`

        :return: a generator of 4-tuples `(old_path, new_path, old_sha, new_sha)`

        Examples:
        - a new file 'setup.py' was created:
            `(None, 'setup.py', None, 'file_sha')`
        - an existing 'setup.py' was deleted:
            `('setup.py', None, 'old_file_sha', None)`
        - setup.py.old was renamed to setup.py, content unchanged:
            `('setup.py.old', 'setup.py', 'file_sha', 'file_sha')`
        - setup.py was edited:
            `('setup.py', 'setup.py', 'old_file_sha', 'new_file_sha')`
        - setup.py.old was edited and renamed to setup.py:
            `('setup.py.old', 'setup.py', 'old_file_sha', 'new_file_sha')`

        Detecting the last one is computationally expensive. You can adjust this
        behaviour by passing the `threshold` parameter, which is 0.5 by default.
        It means that if roughly 50% of the file content is the same,
        it is considered a match. `threshold=1` means that only exact
        matches are considered, effectively disabling this comparison.
        If threshold is set to 0, any pair of deleted and added file will be
        considered renamed and edited; this last case doesn't make much sense so
        don't set it too low.
        """
        if isinstance(parent, str):
            parent = Commit(parent)
        if not isinstance(parent, Commit):
            raise TypeError("parent must be a Commit or a commit hash")

        # # filename: (blob sha before, blob sha after)
        # new_files = self.tree._file_blob_map
        # new_paths = self.tree._file_set
        # old_files = parent.tree._file_blob_map
        # old_paths = parent.tree._file_set

        # !!! We really need to traverse the trees ###
        new_files: Dict[File, Blob] = {}
        for f, b in self.tree.traverse():
            new_files[f] = b
        old_files: Dict[File, Blob] = {}
        for f, b in parent.tree.traverse():
            old_files[f] = b

        # unchanged_paths
        for f in new_files.keys() & old_files.keys():
            if new_files[f] != old_files[f]:
                # i.e. Blob sha Changed!
                yield f, f, old_files[f], new_files[f]

        added_paths: Set[File] = new_files.keys() - old_files.keys()
        deleted_paths: Set[File] = old_files.keys() - new_files.keys()

        if threshold >= 1:  # i.e. only exact matches are considered
            for f in added_paths:  # add
                yield None, f, None, new_files[f]
            for f in deleted_paths:
                yield f, None, old_files[f], None
            return

        if parent.hash not in self._parent_shas:
            warnings.warn(
                "Comparing non-adjacent commits might be "
                "computationally expensive. Proceed with caution."
            )

        # search for matches
        sm = difflib.SequenceMatcher()
        # for each added blob, try to find a match in deleted blobs
        #   if there is a match, signal a rename and remove from deleted
        #   if there is no match, signal a new file
        # unused deleted blobs are indeed deleted
        for added_file, added_blob in new_files.items():
            sm.set_seq1(added_blob.data)
            matched = False
            for deleted_file, deleted_blob in old_files.items():
                sm.set_seq2(deleted_blob.data)
                # use quick checks first (lower bound by length diff)
                if (
                    sm.real_quick_ratio() > threshold
                    and sm.quick_ratio() > threshold
                    and sm.ratio() > threshold
                ):
                    yield deleted_file, added_file, deleted_blob, added_blob
                    del old_files[deleted_file]
                    matched = True
                    break
            if not matched:  # this is a new file
                yield None, added_file, None, added_blob

        for deleted_file, deleted_blob in old_files.items():
            yield deleted_file, None, deleted_blob, None

    def __sub__(self, parent: "Commit"):
        return self.compare(parent)


class File(_NamedObject):
    _ident = "f"

    @property
    def path(self) -> str:
        return self.key

    @property
    def name(self) -> str:
        return self.key.split("/")[-1]

    @cached_property
    def authors(self) -> List[Author]:
        return [Author(a) for a in self._get_list_values("f2a")]

    @cached_property
    def blobs(self) -> List[Blob]:
        return [Blob(b) for b in self._get_list_values("f2b")]

    @cached_property
    def commits(self) -> List[Commit]:
        return [Commit(c) for c in self._get_list_values("f2c")]


class Tree(_GitObject):
    _ident = "t"

    @cached_property
    def data(self) -> str:
        return self.woc.show_content("tree", self.key)

    @property
    def _file_names(self) -> List[str]:
        return [l[1] for l in self.data]

    @cached_property
    def _file_set(self) -> Set[str]:
        return {l[1] for l in self.data}

    @property
    def files(self) -> List["File"]:
        return [File(f) for f in self._file_names]

    @property
    def _blob_shas(self) -> List[str]:
        return [l[2] for l in self.data]

    @cached_property
    def _blob_set(self) -> Set[str]:
        return {l[2] for l in self.data}

    @property
    def blobs(self) -> List["Blob"]:
        return [Blob(b) for b in self._blob_shas]

    @cached_property
    def _file_blob_map(self) -> Dict[str, str]:
        return {l[1]: l[2] for l in self.data}

    def _traverse(self) -> "Generator[Tuple[str, str], None, None]":
        for mode, fname, sha in self.data:
            # trees are always 40000:
            # https://stackoverflow.com/questions/1071241
            if mode != "40000":
                yield fname, sha
            else:
                _logger.debug(f"traverse: into {fname} ({sha})")
                for _fname, _sha in Tree(sha)._traverse():
                    yield fname + "/" + _fname, _sha

    def traverse(self) -> "Generator[Tuple[File, Blob], None, None]":
        for fname, sha in self._traverse():
            yield File(fname), Blob(sha)

    def __contains__(self, item: Union[str, File, Blob]) -> bool:
        if isinstance(item, str):
            return item in self._file_names or item in self._blob_shas
        if isinstance(item, File):
            return item.text in self._file_names
        if isinstance(item, Blob):
            return item.hex in self._blob_shas
        return False

    def __str__(self) -> str:
        return "\n".join([" ".join(l) for l in self.data])

    def __len__(self) -> int:
        return len(self.data)

    def __iter__(self) -> "Generator[Tuple[File, Blob], None, None]":
        for l in self.data:
            yield File(l[1]), Blob(l[2])


class Project(_NamedObject):
    _ident = "p"

    @cached_property
    def _platform_repo(self) -> str:
        URL_PREFIXES = self.woc.config["sites"]
        prefix, body = self.key.split("_", 1)
        if prefix == "sourceforge.net":
            platform = URL_PREFIXES[prefix]
        elif prefix in URL_PREFIXES and "_" in body:
            platform = URL_PREFIXES[prefix]
            body = body.replace("_", "/", 1)
        elif "." in prefix:
            platform = prefix
            body = body.replace("_", "/", 1)
        else:
            platform = "github.com"
            body = self.key.replace("_", "/", 1)
        return platform, body

    @property
    def url(self) -> str:
        """
        Get the URL for a given project URI.

        >>> Project('CS340-19_lectures').url
        'http://github.com/CS340-19/lectures'
        """
        platform, body = self._platform_repo
        URL_PREFIXES = self.woc.config["sites"]
        if platform in URL_PREFIXES:
            return f"https://{URL_PREFIXES[platform]}/{body}"
        return f"https://{platform}/{body}"

    @cached_property
    def authors(self) -> "List[Author]":
        return [Author(a) for a in self._get_list_values(f"{self._ident}2a")]

    @cached_property
    def _commit_shas(self) -> "List[str]":
        return self._get_list_values(f"{self._ident}2c")

    @cached_property
    def _commit_set(self) -> "Set[str]":
        return self._commit_map.keys()

    @cached_property
    def _commit_map(self) -> "Dict[str, Commit]":
        return {c.hash: c for c in self.commits}

    @cached_property
    def commits(self) -> "List[Commit]":
        return [Commit(c) for c in self._commit_shas]

    @cached_property
    def root_projects(self) -> "List[RootProject]":
        return [RootProject(p) for p in self._get_list_values(f"{self._ident}2P")]

    def __contains__(self, item: Union[str, Commit]) -> bool:
        if isinstance(item, str):
            return item in self._commit_set
        elif isinstance(item, Commit):
            return item.hash in self._commit_set
        return False

    @cached_property
    def head(self) -> "Commit":
        """
        Get the HEAD commit of the repository.

        >>> Project('user2589_minicms').head
        Commit(f2a7fcdc51450ab03cb364415f14e634fa69b62c)
        >>> Project('RoseTHERESA_SimpleCMS').head
        Commit(a47afa002ccfd3e23920f323b172f78c5c970250)
        """
        # Sometimes (very rarely) commit dates are wrong, so the latest commit
        # is not actually the head. The magic below is to account for this
        parents = set().union(*(c._parent_shas for c in self.commits))
        heads = [self._commit_map[c] for c in self._commit_set - parents]

        # it is possible that there is more than one head.
        # E.g. it happens when HEAD is moved manually (git reset)
        # and continued with a separate chain of commits.
        # in this case, let's just use the latest one
        # actually, storing refs would make it much simpler
        _heads_sorted = sorted(heads, key=lambda c: c.authored_at or _DAY_Z, reverse=True)
        if len(_heads_sorted) == 0:
            raise ValueError("No head commit found")
        return _heads_sorted[0]

    @cached_property
    def tail(self) -> "Commit":
        """
        Get the first commit SHA by following first parents.

        >>> Project(b'user2589_minicms').tail
        Commit(1e971a073f40d74a1e72e07c682e1cba0bae159b)
        """
        pts = {c._parent_shas[0] for c in self.commits if c._parent_shas}
        for c in self.commits:
            if c.hash in pts and not c._parent_shas:
                return c

    @cached_property
    def earliest_commit(self) -> "Commit":
        """Get the earliest commit of the repository"""
        return min(self.commits, key=lambda c: c.authored_at or _DAY_Z)

    @cached_property
    def latest_commit(self) -> "Commit":
        """Get the latest commit of the repository"""
        return max(self.commits, key=lambda c: c.authored_at or _DAY_Z)

    def commits_fp(self) -> Generator["Commit", None, None]:
        """
        Get a commit chain by following only the first parent.

        Mimic https://git-scm.com/docs/git-log#git-log---first-parent.
        Thus, you only get a small subset of the full commit tree.

        >>> p = Project(b'user2589_minicms')
        >>> set(c.sha for c in p.commits_fp).issubset(p.commit_shas)
        True

        In scenarios where branches are not important, it can save a lot
        of computing.

        Yields:
            Commit: binary commit shas, following first parent only,
                from the latest to the earliest.
        """
        # Simplified version of self.head():
        #   - slightly less precise,
        #   - 20% faster
        #
        # out of 500 randomly sampled projects, 493 had the same head.
        # In the remaining 7:
        #     2 had the same commit chain length,
        #     3 had one more commit
        #     1 had two more commits
        #     1 had three more commits
        # Execution time:
        #   simplified version (argmax): ~153 seconds
        #   self.head(): ~190 seconds

        # at this point we know all commits are in the dataset
        # (validated in __iter___)
        commit = self.latest_commit

        while commit:
            # no point try-except: the truth value of a list is len(list)
            first_parent = commit._parent_shas and commit._parent_shas[0]
            yield commit
            if not first_parent:
                break
            commit = self._commit_map.get(first_parent, Commit(first_parent))

    def __iter__(self) -> "Generator[Commit, None, None]":
        for c in self.commits:
            try:
                if c.author in self.woc.config["ignoredAuthors"]:
                    continue
                yield c
            except KeyError:
                pass

    @property
    def projects(self) -> List["Project"]:
        raise NotImplementedError("Project object does not have projects method")
    
    def download_blob(self, blob_sha: str) -> str:
        """
        Download the blob content from remote.
        """
        try:
            import requests
            from urllib.parse import quote_plus
        except ImportError:
            raise ImportError("This function requires the requests module. Install it via `pip install requests`")

        if self._platform_repo[0] == 'github.com':
            project = self._platform_repo[1]
            _r = requests.get(f'https://api.github.com/repos/{project}/git/blobs/{blob_sha}', 
                    allow_redirects=True,
                    headers={'Accept': 'application/vnd.github.raw+json'})
            _r.raise_for_status()
            return _r.content
        elif self._platform_repo[0] == 'gitlab.com':
            if not hasattr(self, "gitlab_project_id"):
                project = quote_plus(self._platform_repo[1])
                r = requests.get(f'https://gitlab.com/api/v4/projects/{project}')
                r.raise_for_status()
                self.gitlab_project_id = r.json()['id']
            _r = requests.get(f'https://gitlab.com/api/v4/projects/{self.gitlab_project_id}/repository/blobs/{blob_sha}/raw', 
                    allow_redirects=True)
            _r.raise_for_status()
            return _r.content
        else:
            raise NotImplementedError("The function is not implemented for " + self._platform_repo[0])
        

    def save(self, path: str, commit: Optional[Commit] = None):
        """
        Save the project files to the disk. Binary blobs are retrieved from the remote.

        :param path: The path to save the files.
        :param commit: Save the files at this commit. If None, the head or latest commit is used.
        """
        if commit is None:
            try:
                commit = self.head
            except ValueError:
                _logger.warning(f"No head commit found for {self.key}, using latest commit")
                commit = self.latest_commit

        flist = list(commit.tree.traverse())
        for idx, (f, blob) in enumerate(flist):
            _logger.debug(f"{idx + 1}/{len(flist)}: {f.path}")
            _p = os.path.join(path, f.path)
            os.makedirs(os.path.dirname(_p), exist_ok=True)
            with open(_p, 'wb') as f:
                try:
                    f.write(blob.data.encode())
                except KeyError as e:
                    _logger.info(f"Missing blob {blob.key}")
                    try:
                        if self._platform_repo[0] in ('github.com', 'gitlab.com'):
                            f.write(self.download_blob(blob.hash))
                    except Exception as e:
                        _logger.error(f"Failed to download blob {blob.hash}: {e}")
                except Exception as e:
                    _logger.error(f"Failed to write blob {blob.hash}: {e}")


class RootProject(Project):
    _ident = "P"

    @cached_property
    def unique_authors(self) -> "List[Author]":
        return [UniqueAuthor(a) for a in self._get_list_values(f"{self._ident}2A")]

    @cached_property
    def commits(self) -> "List[Commit]":
        return [Commit(c) for c in self._get_list_values(f"{self._ident}2C")]

    @cached_property
    def projects(self) -> "List[Project]":
        return [Project(p) for p in self._get_list_values(f"{self._ident}2p")]

    @property
    def root_projects(self) -> List["RootProject"]:
        raise NotImplementedError("RootProject object does not have root_projects method")
