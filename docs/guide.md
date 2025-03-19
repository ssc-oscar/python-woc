> [!NOTE] This guide is for users who have the access to UTK / PKU WoC servers. If you don't have access, apply [here](https://docs.google.com/forms/d/e/1FAIpQLSd4vA5Exr-pgySRHX_NWqLz9VTV2DB6XMlR-gue_CQm51qLOQ/viewform?vc=0&c=0&w=1&flr=0&usp=mail_form_link) or send an email to [Audris Mockus](mailto:audris@utk.edu).

## Task 1: Install the python package

python-woc is available on PyPI. For most users, the following command is enough:

```bash
python3 -m pip install -U python-woc
```

    Requirement already satisfied: python-woc in /export/data/play/rzhe/miniforge3/lib/python3.10/site-packages (0.2.2)
    Requirement already satisfied: chardet<6.0.0,>=5.2.0 in /export/data/play/rzhe/miniforge3/lib/python3.10/site-packages (from python-woc) (5.2.0)
    Requirement already satisfied: python-lzf<0.3.0,>=0.2.4 in /export/data/play/rzhe/miniforge3/lib/python3.10/site-packages (from python-woc) (0.2.4)
    Requirement already satisfied: tqdm<5.0.0,>=4.65.0 in /export/data/play/rzhe/miniforge3/lib/python3.10/site-packages (from python-woc) (4.66.4)
    [33mWARNING: Error parsing requirements for certifi: [Errno 2] No such file or directory: '/export/data/play/rzhe/miniforge3/lib/python3.10/site-packages/certifi-2023.11.17.dist-info/METADATA'[0m[33m
    [0m

## Task 2: Basic operations

Let's start by initializing a local WoC client:
(If you want to specify the version of maps to query, pass a version parameter to the constructor.)


```python
from woc.local import WocMapsLocal

woc = WocMapsLocal()

# # or specify a version
# woc = WocMapsLocal(version='V')
# woc = WocMapsLocal(version=['V','V3'])
```

What maps are available?


```python

from pprint import pprint

pprint([(m.name, m.version) for m in woc.maps])
```

    [('c2fbb', 'V'),
     ('obb2cf', 'V'),
     ('bb2cf', 'V'),
     ('a2f', 'V'),
     ('a2f', 'T'),
     ('b2A', 'U'),
     ('b2a', 'U'),
     ('A2f', 'V'),
     ('P2a', 'V'),
     ('b2P', 'V'),
     ('b2f', 'V'),
     ('a2P', 'V'),
     ('a2P', 'T'),
     ('b2fa', 'V'),
     ('b2tac', 'V'),
     ('c2p', 'V3'),
     ('c2p', 'V'),
     ('c2pc', 'U'),
     ('c2cc', 'V'),
     ('c2rhp', 'U'),
     ('p2a', 'V'),
     ('ob2b', 'U'),
     ('A2a', 'V'),
     ('A2a', 'U'),
     ('A2a', 'T'),
     ('A2a', 'S'),
     ('a2A', 'V'),
     ('a2A', 'T'),
     ('a2A', 'S'),
     ('c2dat', 'V'),
     ('c2dat', 'U'),
     ('a2c', 'V'),
     ('a2fb', 'T'),
     ('a2fb', 'S'),
     ('P2c', 'V'),
     ('P2c', 'U'),
     ('c2r', 'T'),
     ('c2r', 'S'),
     ('P2p', 'V'),
     ('P2p', 'U'),
     ('P2p', 'T'),
     ('P2p', 'S'),
     ('P2p', 'R'),
     ('c2h', 'T'),
     ('c2h', 'S'),
     ('c2P', 'V'),
     ('c2P', 'U'),
     ('p2P', 'V'),
     ('p2P', 'U'),
     ('p2P', 'T'),
     ('p2P', 'S'),
     ('p2P', 'R'),
     ('A2c', 'V'),
     ('A2c', 'U'),
     ('A2P', 'V'),
     ...]


## Task 3: Determine the author of the parent commit for commit 009d7b6da9c4419fe96ffd1fffb2ee61fa61532a

It's time for some hand on tasks. The python client supports three types of API:

1. `get_values` API: similar to `getValues` perl API, straightforward and simply queries the database;
2. `show_content` API: similar to `showCnt` perl API,
returns the content of the object;
3. `objects` API: more intuitive, caches results, but adds some overhead.

Let's start with the `get_values` API.

```python
# 1. get_values API

woc.get_values('c2ta', 
               woc.get_values('c2pc', '009d7b6da9c4419fe96ffd1fffb2ee61fa61532a')[0])
```




    ['1092637858', 'Maxim Konovalov <maxim@FreeBSD.org>']



Commits are also stored as objects in WoC. Check what is in the object with `show_content`:

```python
# 2. show_content API

woc.show_content('commit', '009d7b6da9c4419fe96ffd1fffb2ee61fa61532a')
```




    ('464ac950171f673d1e45e2134ac9a52eca422132',
     ('dddff9a89ddd7098a1625cafd3c9d1aa87474cc7',),
     ('Warner Losh <imp@FreeBSD.org>', '1092638038', '+0000'),
     ('Warner Losh <imp@FreeBSD.org>', '1092638038', '+0000'),
     "Don't need to declare cbb module.  don't know why I never saw\nduplicate messages..\n")



For users seeking a more wrapped up OOP interface, the `objects` API is for you.

```python
# 3. objects API
from woc.objects import *
init_woc_objects(woc)
Commit('009d7b6da9c4419fe96ffd1fffb2ee61fa61532a').parents[0].author
```




    Author(Maxim Konovalov <maxim@FreeBSD.org>)



## Task 4: Find out who and when first commited "Hello World"


Let's dive deeper into a more real-world senario. Git stores files as blobs, indexed by the SHA-1 hash of the content (with a prefix indicating the type of the object):

```python
from hashlib import sha1

def git_hash_object(data, type_='blob'):
    """Compute the Git object ID for a given type and data.
    """
    s = f'{type_} {len(data)}\0'.encode() + data
    return sha1(s).hexdigest()

git_hash_object(b'Hello, World!\n')
```




    '8ab686eafeb1f44702738c8b0f24f2567c36da6d'


The map `b2fa` tells the original creator of the blob:

```python
# 1. get_values API

t, a, c = woc.get_values('b2fa', git_hash_object(b'Hello, World!\n'))
print('Time:', datetime.fromtimestamp(int(t)))
print('Author:', a)
print('Project:', woc.get_values('c2p', c)[0])
```

    Time: 1999-12-31 19:25:29
    Author: Roberto Cadena Vega <robblack00_7@hotmail.com
    Project: robblack007_scripts-beagleboard



```python
# 2. objects API

t, a, c = Blob('8ab686eafeb1f44702738c8b0f24f2567c36da6d').first_author
print('Time:', t)
print('Author:', a)
print('Project:', c.projects[0].url)
```

    Time: 1999-12-31 19:25:29
    Author: Roberto Cadena Vega <robblack00_7@hotmail.com
    Project: https://github.com/robblack007/scripts-beagleboard


## Task 5: Find the aliases of the author


WoC has algorithms to detect aliases of authors and forks of projects. "A" represents unique author IDs. Here we find the aliases of the author "Roberto Cadena Vega <robblack00_7@hotmail.com>":


```python
# 1. get_values API

woc.get_values('A2a', woc.get_values('a2A', 'Roberto Cadena Vega <robblack00_7@hotmail.com>')[0])
```




    ['Roberto Cadena Vega <robblack00_7@hotmail.com>',
     'robblack007 <robblack00_7@hotmail.com>']



Above is implemented as an attribute of the `Author` object:

```python
# 2. objects API

Author('Roberto Cadena Vega <robblack00_7@hotmail.com>').aliases
```




    [Author(Roberto Cadena Vega <robblack00_7@hotmail.com>),
     Author(robblack007 <robblack00_7@hotmail.com>)]



## Task 6: List the files in 'team-combinatorics_shuwashuwa-server' and save them to a directory

We know tree represents the directory structure of the project at a certain point in time. We can list all the blobs in the tree:

```python
list(Project('team-combinatorics_shuwashuwa-server').head.tree.traverse())
```




    [(File(.github/workflows/build-test.yml),
      Blob(00a33c83a095ff8b4e0a48864234d6c04fbefb69)),
     (File(.github/workflows/upload-artifact.yml),
      Blob(867dec12e7466a31ad3bfdbb67a00b6d6383ae0c)),
     (File(.gitignore), Blob(91cea399a919aaca5bd1c1be0d8a9f309095f875)),
     (File(LICENSE), Blob(f288702d2fa16d3cdf0035b15a9fcbc552cd88e7)),
     (File(README.md), Blob(b98c3d928866e6558793d2aacbca4037480fea5e)),
     (File(doc/Java开发手册（嵩山版）.pdf), Blob(4d4c5cc9a1a3d42b92c3fc169f5215a2e60ad86f)),
     (File(doc/docker.md), Blob(cf4dcb8b40210fbef88d483d26bae16c176bd1d3)),
     (File(doc/github-actions.md), Blob(6b30f9626e9d34750e2b6faf1fada2bd90d1b79d)),
     (File(doc/todo.md), Blob(e54518e2043803c59bcec43a1ed8cba145b7c0ef)),
     (File(doc/webhook.md), Blob(f83a89dd5efcf76017804e793cf7712e0844257e)),
     (File(helpful_tools/database/csv/activity_info.csv),
      Blob(081b5902a8b6fe393c700ebaa0bfe265ccea4dea)),
     (File(helpful_tools/database/csv/activity_time_slot.csv),
      Blob(90d5c2ecac32368d62ea76d65f466a5f1f50eaef)),
    ...]


WoC has every code blob stored in the database. We can save the project to a local directory (binary or missing blobs are fetched on-demand):

```python
Project('team-combinatorics_shuwashuwa-server')\
    .save('local_repo')
```