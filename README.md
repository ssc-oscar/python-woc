# python-woc

<a href="https://pypi.org/project/python-woc/"><img alt="Python package" src="https://img.shields.io/pypi/v/python-woc?logo=python&logoColor=ffde57"/></a> <a href="https://codecov.io/gh/ssc-oscar/python-woc" ><img src="https://codecov.io/gh/ssc-oscar/python-woc/graph/badge.svg?token=WW7XM2YYAU"/></a> <a href="https://github.c om/ssc-oscar/python-woc/actions" ><img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/ssc-oscar/python-woc/test.yml?logo=github"/></a> <a href="https://github.com/ssc-oscar/python-woc/commits"><img alt="GitHub commit activity" src="https://img.shields.io/github/commit-activity/y/ssc-oscar/python-woc?logo=github"/></a> <a href="https://github.com/ssc-oscar/python-woc/contributors"><img alt="GitHub contributors" src="https://img.shields.io/github/contributors-anon/ssc-oscar/python-woc?logo=github&color=%23ffd664"/></a> 

**python-woc** is the python interface to the World of Code (WoC) data.
It precedes the [oscar.py](https://ssc-oscar.github.io/oscar.py) project and is hundreds of times faster than the invoking [lookup](https://github.com/ssc-oscar/lookup) scripts via subprocess.

## What mappings and objects are supported?

Note that python-woc does not support all data types in WoC. It has built-in readers for:

- Tokyo Cabinet hash databases (`.tch` files)
- Stacked Binary files (`.bin` files)

Gzipped files (`.s/.gz`, e.g. `PYthruMaps/c2bPtaPkgOPY.0.gz`) are not supported yet, because currently it makes no sense to manipulate them natively in Python. Instead, you should refer to [WoC tutorial](https://github.com/woc-hack/tutorial?tab=readme-ov-file#activity-3---investigate-the-maps) and decompress them into a pipe, and deal them with command line utilities.

Mappings below are supported by both `woc.get_values` and `woc.objects`:

```python
['A2P', 'A2a', 'A2b', 'A2c', 'A2f', 'A2fb', 'P2A', 'P2a', 'P2c', 'P2p', 'a2A', 'a2P', 'a2b', 'a2c', 'a2f', 'a2p', 'b2P', 'b2c', 'b2f', 'b2fa', 'b2tac', 'bb2cf', 'c2P', 'c2b', 'c2cc', 'c2dat', 'c2f', 'c2fbb', 'c2h', 'c2p', 'c2pc', 'c2r', 'c2ta', 'f2a', 'f2b', 'f2c', 'obb2cf', 'p2P', 'p2a', 'p2c']
```

And objects:

```python
['commit', 'tree', 'blob']
```

If you are still unsure what characters in the mappings mean, checkout the [WoC Tutorial](https://github.com/woc-hack/tutorial?tab=readme-ov-file#activity-3---investigate-the-maps).

## Requirements

- Linux with a GNU toolchain (only tested on x86_64, Ubuntu / CentOS)

- Python 3.8 or later

## Install python-woc

### From PyPI

The latest version of `python-woc` is available on PyPI and can be installed using `pip`:

```bash
pip3 install python-woc
```

### From Source

To try out latest features, you may install python-woc from source:

```bash
git clone https://github.com/ssc-oscar/python-woc.git
cd python-woc
python3 -m pip install -r requirements.txt
python3
```

## Generate Profiles

One of the major improvents packed in python-woc is profile. Profiles tell the driver what versions of what maps are available, decoupling the driver from the folder structure of the data. It grants the driver the ability to work with multiple versions of WoC, on a different machine, or even on the cloud.

Profiles are generated using the `woc.detect` script. The script takes a list of directories, scans for matched filenames, and generates a profile:

```bash
python3 woc.detect /path/to/woc/1 /path/to/woc/2 ... > wocprofile.json
```

By default, python-woc looks for `wocprofile.json`, `~/.wocprofile.json`, and `/etc/wocprofile.json` for the profile. 

## Use CLI

python-woc's CLI is a drop-in replacement for the `getValues` and `showCnt` perl scripts. We expect existing scripts to be work just well with the following:

```bash
alias getValues='python3 -m woc.get_values'
alias showCnt='python3 -m woc.show_content'
```

The usage is the same as the original scripts, and the output should be identical:

```bash
# echo some_key | echo python3 -m woc.get_values some_map
> echo e4af89166a17785c1d741b8b1d5775f3223f510f | showCnt commit 3
tree f1b66dcca490b5c4455af319bc961a34f69c72c2
parent c19ff598808b181f1ab2383ff0214520cb3ec659
author Audris Mockus <audris@utk.edu> 1410029988 -0400
committer Audris Mockus <audris@utk.edu> 1410029988 -0400

News for Sep 5
```

You may find more examples in the [lookup](https://github.com/ssc-oscar/lookup#ov-readme) repository.
If you find any incompatibilities, please [submit an issue report](https://github.com/ssc-oscar/python-woc/issues/new).

## Use Python API

The python API is designed to get rid of the overhead of invoking the perl scripts via subprocess. It is also more native to python and provides a more intuitive interface.

With a `wocprofile.json`, you can create a `WocMapsLocal` object and access the maps in the file system:

```python
>>> from woc.local import WocMapsLocal
>>> woc = WocMapsLocal()  # or use only the version R: woc = WocMapsLocal(version="R")
>>> woc.maps
{'p2c', 'a2b', 'c2ta', 'a2c', 'c2h', 'b2tac', 'a2p', 'a2f', 'c2pc', 'c2dat', 'b2c', 'P2p', 'P2c', 'c2b', 'f2b', 'b2f', 'c2p', 'P2A', 'b2fa', 'c2f', 'p2P', 'f2a', 'p2a', 'c2cc', 'f2c', 'c2r', 'b2P'}
```

To query the maps, you can use the `get_values` method:

```python
>>> woc.get_values("b2fa", "05fe634ca4c8386349ac519f899145c75fff4169")
('1410029988', 'Audris Mockus <audris@utk.edu>', 'e4af89166a17785c1d741b8b1d5775f3223f510f')
>>> woc.get_values("c2b", "e4af89166a17785c1d741b8b1d5775f3223f510f")
['05fe634ca4c8386349ac519f899145c75fff4169']
>>> woc.get_values("b2tac", "05fe634ca4c8386349ac519f899145c75fff4169")
[('1410029988', 'Audris Mockus <audris@utk.edu>', 'e4af89166a17785c1d741b8b1d5775f3223f510f')]
```

Use `show_content` to get the content of a blob, a commit, or a tree:

```python
>>> woc.show_content("tree", "f1b66dcca490b5c4455af319bc961a34f69c72c2")
[('100644', 'README.md', '05fe634ca4c8386349ac519f899145c75fff4169'), ('100644', 'course.pdf', 'dfcd0359bfb5140b096f69d5fad3c7066f101389')]
>>> woc.show_content("commit", "e4af89166a17785c1d741b8b1d5775f3223f510f")
('f1b66dcca490b5c4455af319bc961a34f69c72c2', ('c19ff598808b181f1ab2383ff0214520cb3ec659',), ('Audris Mockus <audris@utk.edu>', '1410029988', '-0400'), ('Audris Mockus <audris@utk.edu>', '1410029988', '-0400'), 'News for Sep 5')
>>> woc.show_content("blob", "05fe634ca4c8386349ac519f899145c75fff4169")
'# Syllabus for "Fundamentals of Digital Archeology"\n\n## News\n\n* ...'
```

Note that the function yields different types for different maps. Please refer to the [documentation](https://ssc-oscar.github.io/python-woc) for details.

Sometimes you may want to know the exact size of WoC, doing so is easy and quick with `count`:

```python
>>> woc.count("blob")  # count the number of blobs
17334020520
>>> woc.count("A2P")  # count the number of unique authors
44613280
```

## Use Python Objects API

The objects API provides a more intuitive way to access the WoC data. 
Note that the objects API is not a replacement to [oscar.py](https://ssc-oscar.github.io/oscar.py) even looks pretty much like the same: many of the methods have their signatures changed and refactored to be more consistent, intuitive and performant. Query results are cached, so you can access the same object multiple times without additional overhead. 

Call `init_woc_objects` to initialize the objects API with a WoC instance:

```python
from woc.local import WocMapsLocal
from woc.objects import init_woc_objects
woc = WocMapsLocal()
init_woc_objects(woc)
```

To get the tree of a commit:

```python
from woc.objects import Commit
>>> c1 = Commit("91f4da4c173e41ffbf0d9ecbe2f07f3a3296933c")
>>> c1.tree
Tree(836f04d5b374033b1608269e2f3aaabae263a0db)
>>> c1.projects[0].url
'https://github.com/woc-hack/thebridge'
```

For more, check `woc.objects` in the documentation.

## Contributing

We welcome awesome contributions from the community. If you are motivated to add new features or fix bugs, please refer to the [contributing guide](https://ssc-oscar.github.io/python-woc/woc.html#to-contribute).