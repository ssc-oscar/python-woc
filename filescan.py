import os
import re
import logging
from typing import Optional, Set, Union, Dict, Tuple

_basemap_pat = re.compile(r'^(\w+)2(\w+)Full(\w+)(?:.(\d+))?.tch$')
def parse_basemap_path(fname: str):
    """
    Parse basemap filename into (src, dst, ver, idx)
    >>> parse_basemap_path('c2fFullR.3.tch')
    ('c', 'f', 'R', '3')
    >>> parse_basemap_path('c2fFullR.tch')
    ('c', 'f', 'R', None)
    """
    m = _basemap_pat.match(fname)
    if not m or len(m.groups()) != 4:
        raise ValueError(f'Invalid path: {fname}')
    return m.groups()

_sha1map_pat = re.compile(r'^([\w\.]+)_(\d+).(\w+)$')
def parse_sha1map_path(fname: str):
    """
    Parse sha1map (sha1o/sha1c/blob) filename into (name, idx, ext)
    >>> parse_sha1map_path('commit_0.tch')
    ('commit', '0', 'tch')
    >>> parse_sha1map_path('blob_0.idx')
    ('blob', '0', 'idx')
    >>> parse_sha1map_path('sha1.blob_0.bin')
    ('sha1.blob', '0', 'bin')
    """
    m = _sha1map_pat.match(fname)
    if not m or len(m.groups()) != 3:
        raise ValueError(f'Invalid path: {fname}')
    return m.groups()

_short_name_to_full = {
    'a': 'author',
    'A': 'author_dealised',
    'b': 'blob',
    'c': 'commit',
    'cc': 'child_commit',
    'f': 'file',
    'fa': 'first_author',
    't': 'tree',
    'h': 'head',
    'p': 'project',
    'P': 'project_deforked',
    'pc': 'parent_commit',
    'r': 'root_commit',
    'ta': 'time_author',
    'tac': 'time_author_commit',
    'trp': 'torvalds_path',
    'dat': 'colon_seperated_data',
    'tch': 'compressed_data',
    'bin': 'binary_data',
    'idx': 'binary_index'
}

# match (name)Full(ver).(idx).tch

_full_name_to_short = {v: k for k, v in _short_name_to_full.items()}

##### module configuration variables #####

# default config values
DEFAULT_BASE_PATH = '/woc'
DEFAULT_STORES = {
    'OSCAR_ALL_BLOBS': 'All.blobs',
    'OSCAR_ALL_SHA1C': 'All.sha1c',
    'OSCAR_ALL_SHA1O': 'All.sha1o',
    'OSCAR_BASEMAPS': 'basemaps',
}

# tokyo cabinet store paths
PATHS: Dict[Tuple[str, str], Tuple[str, int, Optional[str]]] = {}

# prefixes used by World of Code to identify source project platforms
# See Project.to_url() for more details
# Prefixes have been deprecated by replacing them with the string resembling
# actual URL
URL_PREFIXES = {
    b'bitbucket.org': b'bitbucket.org',
    b'gitlab.com': b'gitlab.com',
    b'android.googlesource.com': b'android.googlesource.com',
    b'bioconductor.org': b'bioconductor.org',
    b'drupal.com': b'git.drupal.org',
    b'git.eclipse.org': b'git.eclipse.org',
    b'git.kernel.org': b'git.kernel.org',
    b'git.postgresql.org': b'git.postgresql.org',
    b'git.savannah.gnu.org': b'git.savannah.gnu.org',
    b'git.zx2c4.com': b'git.zx2c4.com',
    b'gitlab.gnome.org': b'gitlab.gnome.org',
    b'kde.org': b'anongit.kde.org',
    b'repo.or.cz': b'repo.or.cz',
    b'salsa.debian.org': b'salsa.debian.org',
    b'sourceforge.net': b'git.code.sf.net/p'
}
IGNORED_AUTHORS = (
    b'GitHub Merge Button <merge-button@github.com>'
)

def set_config(
        base_path: str = DEFAULT_BASE_PATH,
        stores: Optional[Dict[str, str]] = None,
        url_prefixes: Optional[Dict[bytes, bytes]] = None,
        ignored_authors: Optional[Tuple[bytes]] = None
    ):
    """Set the configuration for the Oscar module.
    :param base_path: path to the woc directory
    :param stores: a dictionary of store names (OSCAR_ALL_BLOBS, OSCAR_ALL_SHA1C, OSCAR_ALL_SHA1O, OSCAR_BASEMAPS)
        to their relative paths in the woc directory
    :param url_prefixes: a BYTES dictionary of url prefixes to their full urls (e.g. b'bitbucket.org' -> b'bitbucket.org')
    :param ignored_authors: a BYTES tuple of authors to ignore (e.g. b'GitHub Merge Button <merge-button@github.com>'
    """

    global PATHS, IGNORED_AUTHORS, URL_PREFIXES

    if not os.path.exists(base_path):
        raise ValueError(f'Oscar failed to locate {base_path},'
            'please call set_config("/path/to/woc")')

    if stores is None:
        stores = {k: os.path.join(base_path, v) for k, v in DEFAULT_STORES.items()}

    # Scan the woc data directory
    for store_name, store_path in stores.items():
        for f in os.listdir(store_path):
            try:
                if store_name == 'OSCAR_BASEMAPS':
                    src, dst, ver, idx = parse_basemap_path(f)
                    k = (src, dst)
                    prefix_len = int(idx).bit_length() if idx else 0
                    if k in PATHS:
                        _, _predix_len, _ver = PATHS[k][0], PATHS[k][1], PATHS[k][2]
                        if _ver > ver or (_ver == ver and _predix_len >= prefix_len):
                            continue
                    PATHS[k] = (
                        os.path.join(store_path, 
                            f.replace(idx, '{key}') if idx else f
                        ), prefix_len, ver)
                    pass
                elif store_name in ('OSCAR_ALL_BLOBS', 'OSCAR_ALL_SHA1C', 'OSCAR_ALL_SHA1O'):
                    name, idx, ext = parse_sha1map_path(f)
                    try:
                        src = _full_name_to_short[name.replace('sha1.','')]
                    except KeyError:
                        raise ValueError(f'Invalid file type: {name}')
                    k = (src, ext)
                    prefix_len = int(idx).bit_length() if idx else 0
                    if k in PATHS:
                        _, _predix_len = PATHS[k][0], PATHS[k][1]
                        if _predix_len >= prefix_len:
                            continue
                    PATHS[k] = (
                        os.path.join(store_path, 
                            f.replace(idx, '{key}') if idx else f
                        ), prefix_len, None)
                else:
                    raise ValueError(f'Invalid store name: {store_name}, expected one of {DEFAULT_STORES.keys()}')
            
            except ValueError as e:
                logging.warning(f'Cannot parse {f}: {repr(e)} ')

    print(f'Loaded {len(PATHS.keys())} maps: '
        f'{[_short_name_to_full[x[0]] + "->" + _short_name_to_full[x[1]] + ":" + str(PATHS[x]) for x in PATHS.keys()]}')

    if url_prefixes is not None:
        URL_PREFIXES = url_prefixes

    if ignored_authors is not None:
        IGNORED_AUTHORS = ignored_authors

# run set_config on import
set_config()

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
    print(PATHS)