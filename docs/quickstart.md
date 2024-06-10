## Install

### From PyPI

```bash
python3 -m pip install python-woc
```

### From Source

```bash
git clone https://github.com/ssc-oscar/python-woc.git
python3 -m pip install .
```

## Generate Profiles

```bash
python3 woc.detect /path/to/woc/1 /path/to/woc/2 ... > wocprofile.json
```

## CLI

```bash
echo some_key | echo python3 -m woc.get_values some_map
```

## Python API

```python
from woc.local import WocMapsLocal
woc = WocMapsLocal()  # by default it uses ./wocprofile.json, ~/.wocprofile.json, /etc/wocprofile.json
v1 = woc.get_values('some_map', 'some_key')
v2 = woc.show_content('some_commit', 'some_sha')
```

## Python OOP API

```python
from woc.local import WocMapsLocal
from woc.objects import Commit, init_woc_objects
woc = WocMapsLocal()
init_woc_objects(woc)
c = Commit('some_sha')
c.tree  
```
