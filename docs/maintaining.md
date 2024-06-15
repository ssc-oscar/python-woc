## What mappings and objects are supported?

python-woc includes tch adapters

```python
['A2P', 'A2a', 'A2b', 'A2c', 'A2f', 'A2fb', 'P2A', 'P2a', 'P2c', 'P2p', 'a2A', 'a2P', 'a2b', 'a2c', 'a2f', 'a2p', 'b2P', 'b2c', 'b2f', 'b2fa', 'b2tac', 'bb2cf', 'c2P', 'c2b', 'c2cc', 'c2dat', 'c2f', 'c2fbb', 'c2h', 'c2p', 'c2pc', 'c2r', 'c2ta', 'f2a', 'f2b', 'f2c', 'obb2cf', 'p2P', 'p2a', 'p2c']
```

```python
['commit', 'tree', 'blob']
```

## Generate profiles for a local WoC instance

```bash
python3 -m woc.detect /path/to/woc/1 /path/to/woc/2 > wocprofile.json
```

## Add a mapping to python-woc

### `woc.get_values`

TODO


### `woc.show_content`

TODO

### `woc.objects`

TODO