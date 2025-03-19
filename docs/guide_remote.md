### Task 1: Install the python package

Starting from 0.3.0, python-woc supports the HTTP API! You are not limited by the access to PKU or UTK servers. 
First, let us install or upgrade the python package:


```python
!python3 -m pip install -U python-woc
```

    Looking in indexes: https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
    Requirement already satisfied: python-woc in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (0.3.0)
    Requirement already satisfied: chardet<6.0.0,>=5.2.0 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from python-woc) (5.2.0)
    Requirement already satisfied: httpx<0.29.0,>=0.28.1 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from python-woc) (0.28.1)
    Requirement already satisfied: python-lzf<0.3.0,>=0.2.4 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from python-woc) (0.2.4)
    Requirement already satisfied: rapidgzip<0.15.0,>=0.14.3 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from python-woc) (0.14.3)
    Requirement already satisfied: tqdm<5.0.0,>=4.65.0 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from python-woc) (4.66.4)
    Requirement already satisfied: anyio in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from httpx<0.29.0,>=0.28.1->python-woc) (4.5.2)
    Requirement already satisfied: certifi in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from httpx<0.29.0,>=0.28.1->python-woc) (2025.1.31)
    Requirement already satisfied: httpcore==1.* in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from httpx<0.29.0,>=0.28.1->python-woc) (1.0.7)
    Requirement already satisfied: idna in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from httpx<0.29.0,>=0.28.1->python-woc) (3.10)
    Requirement already satisfied: h11<0.15,>=0.13 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from httpcore==1.*->httpx<0.29.0,>=0.28.1->python-woc) (0.14.0)
    Requirement already satisfied: sniffio>=1.1 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from anyio->httpx<0.29.0,>=0.28.1->python-woc) (1.3.1)
    Requirement already satisfied: exceptiongroup>=1.0.2 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from anyio->httpx<0.29.0,>=0.28.1->python-woc) (1.2.1)
    Requirement already satisfied: typing-extensions>=4.1 in /home/hrz/mambaforge/envs/woc/lib/python3.8/site-packages (from anyio->httpx<0.29.0,>=0.28.1->python-woc) (4.12.2)


### Task 2 (Optional): Generate an API key

This is an optional step but I recommend you to do it. By default HTTP API restricts the number of requests per minute to avoid abuse. To raise the limit, you can generate an API key on the World of Code website.

Currently the website is at: https://woc.osslab-pku.org/ (After we figure out the domain transfer, it will probably be moved to https://worldofcode.org/)

The API key is a string like `woc-XXXXXXXXXXXXXX-YYYYYYYYYYYYYY`, and you pass it to the client with the `api_key` argument:

```python
# sync client
woc = WocMapsRemote(
    base_url="https://woc.osslab-pku.org/api/",
    api_key="woc-XXXXXXXXXXXXXX-YYYYYYYYYYYYYY"
)
# async client
woca = WocMapsRemoteAsync(
    base_url="https://woc.osslab-pku.org/api/",
    api_key="woc-XXXXXXXXXXXXXX-YYYYYYYYYYYYYY"
)
```

### Task 3: Use the python package

The sync remote client feels the same as the local client, and most APIs will just work:


```python
from woc.remote import WocMapsRemote

woc = WocMapsRemote(
    base_url="https://woc.osslab-pku.org/api/",  # <- may be different for you
)
[(m.name, m.version) for m in woc.maps]
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
     ('a2A', 'V0'),
     ('a2A', 'V3'),
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
     ...]




```python
# get_values API

woc.get_values('c2ta', 
               woc.get_values('c2pc', '009d7b6da9c4419fe96ffd1fffb2ee61fa61532a')[0])
```




    ['1092637858', 'Maxim Konovalov <maxim@FreeBSD.org>']




```python
# show_content API

woc.show_content('commit', '009d7b6da9c4419fe96ffd1fffb2ee61fa61532a')
```




    ['464ac950171f673d1e45e2134ac9a52eca422132',
     ['dddff9a89ddd7098a1625cafd3c9d1aa87474cc7'],
     ['Warner Losh <imp@FreeBSD.org>', '1092638038', '+0000'],
     ['Warner Losh <imp@FreeBSD.org>', '1092638038', '+0000'],
     "Don't need to declare cbb module.  don't know why I never saw\nduplicate messages..\n"]



The only exception is `all_keys` API, which is not supported by the remote client (I did not find a way to paginate that.)


```python
# Objects API

from woc.objects import *
init_woc_objects(woc)

Commit('009d7b6da9c4419fe96ffd1fffb2ee61fa61532a').parents[0].author
```




    Author(Maxim Konovalov <maxim@FreeBSD.org>)




```python
woc.all_keys('c2p')
```


    ---------------------------------------------------------------------------

    NotImplementedError                       Traceback (most recent call last)

    Cell In[6], line 1
    ----> 1 woc.all_keys('c2p')


    File ~/mambaforge/envs/woc/lib/python3.8/site-packages/woc/remote.py:333, in WocMapsRemote.all_keys(self, map_name)
        332 def all_keys(self, map_name: str) -> Generator[bytes, None, None]:
    --> 333     return self._asyncio_run(super().all_keys(map_name))


    File ~/mambaforge/envs/woc/lib/python3.8/site-packages/woc/remote.py:292, in WocMapsRemote._asyncio_run(self, coro, timeout)
        285 def _asyncio_run(self, coro: Awaitable, timeout=30):
        286     """
        287     Runs the coroutine in an event loop running on a background thread, and blocks the current thread until it returns a result. This plays well with gevent, since it can yield on the Future result call.
        288 
        289     :param coro: A coroutine, typically an async method
        290     :param timeout: How many seconds we should wait for a result before raising an error
        291     """
    --> 292     return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=timeout)


    File ~/mambaforge/envs/woc/lib/python3.8/concurrent/futures/_base.py:444, in Future.result(self, timeout)
        442     raise CancelledError()
        443 elif self._state == FINISHED:
    --> 444     return self.__get_result()
        445 else:
        446     raise TimeoutError()


    File ~/mambaforge/envs/woc/lib/python3.8/concurrent/futures/_base.py:389, in Future.__get_result(self)
        387 if self._exception:
        388     try:
    --> 389         raise self._exception
        390     finally:
        391         # Break a reference cycle with the exception in self._exception
        392         self = None


    File ~/mambaforge/envs/woc/lib/python3.8/site-packages/woc/remote.py:261, in WocMapsRemoteAsync.all_keys(self, map_name)
        260 async def all_keys(self, map_name: str) -> Generator[bytes, None, None]:
    --> 261     raise NotImplementedError(
        262         "all_keys is not implemented in WoC HTTP API. "
        263         "If you feel it is necessary, please create a feature request at "
        264         "https://github.com/ssc-oscar/python-woc/issues/new"
        265     )


    NotImplementedError: all_keys is not implemented in WoC HTTP API. If you feel it is necessary, please create a feature request at https://github.com/ssc-oscar/python-woc/issues/new


### Task 4: Batching

Git objects are typically small, and sending dozens of small queries is not efficient. The remote client supports batching by `show_content_many` and `get_values_many`, it will send 10 queries in one request. For the impatient, it displays a progress bar with `progress=True`. The return value is a tuple of 2 dictionaries { results }, { errors }.



```python
woc.show_content_many('commit', woc.get_values('a2c', 'Audris Mockus <audris@utk.edu>')[:50], progress=True)
```

    100%|██████████| 5/5 [00:00<00:00,  5.45it/s]





    ({'001ec7302de3b07f32669a1f1faed74585c8a8dc': ['d0074dfdf50faf1a679a293d1833af74513d5b38',
       ['13710ca2439f85eff9922169a4588da64b3f1fce'],
       ['Audris Mockus <audris@utk.edu>', '1514659483', '-0500'],
       ['Audris Mockus <audris@utk.edu>', '1514659483', '-0500'],
       'work on diff performance\n'],
      '0037d5c34c2787f2a0b619c5d2a1f76254ac974c': ['ac14b680a6c58f50221b8da7cfa307528b5b971a',
       ['87ec9a9e6fda18cdcb8bd78a0e909afd0e40d329',
        '5fee5205917fa803036a17aba185a0a8af17d1fa'],
       ['Audris Mockus <audris@utk.edu>', '1629765554', '-0400'],
       ['GitHub <noreply@github.com>', '1629765554', '-0400'],
       'Merging 43\n\n'],
      '003f2b790d6fb83924649d90867f3d1545ea0e36': ['3eda5f06cba2c0051367de6ebcf1daf9c3a9cdc6',
       ['8750edd4576f6a0b592a36d777f09d272c42097b',
        'a4ac9e07db0a27268584d2912ddf2cceaf3dc3d2'],
       ['Audris Mockus <audris@utk.edu>', '1512787832', '-0500'],
       ['GitHub <noreply@github.com>', '1512787832', '-0500'],
       'Merge pull request #1 from dylanrainwater/master\n\nCreate drainwa1.md'],
      '00448b8ca4198a41b64618e4f0f9726d206fce69': ['ba20c6b9a6cafb42dcfd01f71a01140639e4a5ea',
       ['37ed4871d1578a9f02169a2bef5e612d465c3c4f'],
       ['Audris Mockus <audris@utk.edu>', '1571281741', '-0400'],
       ['Audris Mockus <audris@utk.edu>', '1571281741', '-0400'],
       'autodeducing types\n'],
      '005905285ff1b9e33babbacfce09f39484e9428b': ['64a63070bb2b9a01707535e8509c80c2e4674e3f',
       [],
       ['Audris Mockus <audris@utk.edu>', '1581825750', '-0500'],
       ['Audris Mockus <audris@utk.edu>', '1581825750', '-0500'],
       'examples on how to do api embedding via doc2vec\n'],
      '00616e51919581ebd84fcb14f26282e963e8a6cd': ['5a573140144efb4f0f987b61e8ff23de1ddef80a',
       ['c5bd344bdd75c3b707ad9d821026bc2ba382c0bb'],
       ['Audris Mockus <audris@utk.edu>', '1516821061', '-0500'],
       ['Audris Mockus <audris@utk.edu>', '1516821061', '-0500'],
       'make sure integers are packed\n'],
      '0064fd6ca213b387347f10de2457ed94d0cf798a': ['21f231a310838a4bef9f8db26e06baabf553b9d7',
       ['2d6fa88a0f45806283b4b0ab987d59bebfd3b9d8'],
       ['Audris Mockus <audris@utk.edu>', '1631804415', '-0400'],
       ['GitHub <noreply@github.com>', '1631804415', '-0400'],
       'Update README.md'],
      '006d7e83e272d1715b2aca1a43e91b9141227532': ['b1423403b051f56afe79662b0222ddca7789e88b',
       ['cb83bea9dcdfb0364796f5f54403767cedf90c5a'],
       ['Audris Mockus <audris@utk.edu>', '1473861546', '+0000'],
       ['Audris Mockus <audris@utk.edu>', '1473861546', '+0000'],
       'README.md edited online with Bitbucket'],
      '007c4f4867e5a27971b056ddcd9b7abc7221f231': ['651a93de99df7e87f98d290292353d4af211c05c',
       ['aa35f02cb9eef14bfcdc354f21bd6e1499519f3e'],
       ['Audris Mockus <audris@utk.edu>', '1550241863', '-0500'],
       ['Audris Mockus <audris@utk.edu>', '1550241863', '-0500'],
       'Current status\n'],
      ...},
     {})




```python
woc.get_values_many('c2b', woc.get_values('P2c', 'user2589_minicms')[:50], progress=True)

```

    100%|██████████| 5/5 [00:00<00:00,  5.56it/s]





    ({'05cf84081b63cda822ee407e688269b494a642de': ['03d1977aecf31666578422805c60cf61562ceea1',
       '1619cce13ffcc3eaaddb1f714072914625f576f6',
       '1838ded6411e5fbfd9d0168de007de3e78e94d94',
       '3993b20337e33a36c9125d139f1f53a279a4c128',
       '3dd682cbf7fd0c482d31f0e74e9ed05e4853cd9f',
       '44a07afd30f499cdba30847094a1e92f13e1320e',
       '6ad59f8158da5afca559c5b3d422af2b1a17eb81',
       '6b0af6a378d95ac9a11297fe83baca147c7af4c2',
       '70ce71f3cd86c10b11b778e502ca9364b2262d8f',
       '83d5c112f8584c5a7f2db377e5dda2216586f2ca',
       '9599aebf9b3cae84678ef0703e6217d47030b0ff',
       'dae40a15a0f5eaef5259d66defe3544166da59bd',
       'e8b638f1548c5b74e2bb4b74d3aaf8da93e24aa1'],
      '086a622f0e24feb7853c520f965f04c7fc7e4861': ['773e50f6785dafd0acbe050e7dd16a8179297652',
       'ad4d743e78a5ceb39942675cf968c1dcaa935557',
       'e87238845f6b48d16807cb4d56a58bd17ab41931'],
      '0ad5b0b392ed22cef866de5ae8504462183b0316': ['29f38813ea514935bce39d8b24c31e486d033340'],
      '104b8284ba6435a3c07eb5ce82f15cb0f956eda3': ['c11edc429d433037a18d346dad544731809f6898'],
      '1837bfa6553a9f272c5dcc1f6259ba17357cf8ed': ['1b92e22ab92e429615d8fdf84353ece7233f2487',
       '870c07dbfaccf8faa87a32efb63d6ae67b37c539',
       '8f0f90c29f067e20ebaf0c53c02c66b89a31e5c3',
       '973a78a1fe9e69d4d3b25c92b3889f7e91142439',
       'a43bb729c565ea9ce17a26d23d68b88030a84aa5',
       'c8da2827d7ed589656075db8c083f5e5ba6d81d9',
       'dca8d68784e46f66ec548c5dab7a0bfbdeaaf5a9'],
      '19ddf6dafb6014c954253bd022778051213ccd9a': ['56aecae2b6137a3d62bdde0c36ea755d48643dc5'],
      '1d3038eab8cac1e8a9df187d411fbc0e4a317270': ['028b4844ea03bfb07bad74efe0aa800464835f1c',
       'dfadce9d6f708fc79711f7e10453ad5584b925e0'],
      '1e971a073f40d74a1e72e07c682e1cba0bae159b': ['1e0eaec8f6164cb5e15031fee8702a05dec6a1cf',
       '2060f551336795224535caa172703b6c0e660510',
       '2bdf5d686c6cd488b706be5c99c3bb1e166cf2f6',
       '7e2a34e2ec9bfdccfa01fff7762592d9458866eb',
       'c006bef767d08b41633b380058a171b7786b71ab',
       'e0ac96cefe3d230553931c54a79fa164a8fa11da',
       'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'],
      '1eda863abed481df83c680a6c31fad05719b166b': ['9300f6dfdbff157aa7a28a42331c334b36302c9d'],
      '27f6af62ff6facfb21a7fe33cddfc115f93cb75f': ['51f9f7da85518d034176fe3a1d5d9eacf0bbaed7',
       'f25b48beb98cfb011373517f23883dd4dbaab589'],
      '2881cf0080f947beadbb7c240707de1b40af2747': ['3bbb2f13dcfbc1c4352c940f8d3c22c2789c621d',
       'c3bfa5467227e7188626e001652b85db57950a36'],
      '2c02c1f9b1a959c5228bf8cfad1a09fd5489b381': ['2cfbd298f18a75d1f0f51c2f6a1f2fcdf41a9559',
       '6365ac91afdde2db36d7c8e7119c5a4cc04d9a2a',
       '6481ac0fbbd735752710018df1ddae0cc926d5c5',
       '64fd4dcec034e966cfc240008d93cc300f878def',
       'e6edff07e43858eb6c1ac618d7956d1dff8f4be8',
       'f796acbf50001003f398f53be27d947acbaa76bf'],
      '3303b05caf2f9b51fc6323820fe9e04780c40e48': ['9be0d9635e048fb5239e1b893adebe6b94cf1942',
       '9eaec93fea6c0f22d6138dd33fa6750d1a9556a9',
       'a932689dd969fc2d6a3c16664021cca7f7e8967a',
       'e048cddd988918af374a4a253017c4d8133c29c0'],
      '335aeff4c90d4d31562a24b2648ed529ef664664': ['070cdd1f69532a37dfc434153f6e887376a68f68'],
      '3b0cbf364870cd35d9e41630387d97393fea2fa5': ['e263e29d9fcd7168498f290560f49de58b69fb57'],
      '3beec34c51d9ae5d60c7eb976bb03a95db235514': ['df8a84af3a9db52a5ee2bf8afd0a120e7e7aecc4'],
      '3c57cd4791ac46ccb73cc22a50d9a4c77e5cd0a3': ['5f41f1fa0952ca9adcfc88d89617e102454a8447'],
      '3c59a5aca8ee3e201977558fe9f1ea5489d2b1b3': ['5c6802269104f3f5a8a831ed70b2170eb94cc46c'],
      '3f68ba216c938e93aff1dc45b241511a0fa94e51': ['028b4844ea03bfb07bad74efe0aa800464835f1c',
       'dfadce9d6f708fc79711f7e10453ad5584b925e0'],
      '4dffda766eba4f4edc31eb0b7691cc75d7775de0': ['409c292ddf48ceedc69cc96c59325dbf6226e287'],
      '58898751944b69ffc04d148b0917473e2d5d5db8': ['1f3e4f03f555d640d72ac4e89d2c8c97bc6255f1',
       '56aecae2b6137a3d62bdde0c36ea755d48643dc5',
       '5f41f1fa0952ca9adcfc88d89617e102454a8447',
       '773e50f6785dafd0acbe050e7dd16a8179297652',
       '958efc14c7d74d732eac137af7e554795dbfe6fc',
       '96bc275bee57ddbe38acbd46776d907bc10f279f',
       '9825f4f761657f2a8cc1352f2a5cd50a442fb624',
       '9eaec93fea6c0f22d6138dd33fa6750d1a9556a9',
       'a400c114785031e934d3a323c247c697f944ba04',
       'a932689dd969fc2d6a3c16664021cca7f7e8967a',
       'ad4d743e78a5ceb39942675cf968c1dcaa935557',
       'e043781b07bbf336f1b9bb7a2c5c1cd60c00c046',
       'e048cddd988918af374a4a253017c4d8133c29c0',
       'e69de29bb2d1d6434b8b29ae775ad8c2e48c5391'],
      '5b0afd26ed90f8b3352f4ac8a53da9f23597c42d': ['4ab32146cbd1c0ba24564b28cbda8b70bc571dda',
       'daae152bed904558cd06cd5ed8da995d818d1eb5',
       'e043781b07bbf336f1b9bb7a2c5c1cd60c00c046'],
      '63ff96cbb38687e68cb4fdd7e208aa70f66ba252': ['df10ebd07b711886fa9a7f9b4569ca5778e187d7'],
      '66acf0a046a02b48e0b32052a17f1e240c2d7356': ['a7227f22a261aec4824b4657d381ab49bce35005',
       'd05d461b48a8a5b5a9d1ea62b3815e089f3eb79b',
       'd1d952ee766d616eae5bfbd040c684007a424364',
       'fcff510d9cc6217b45c1aca343bba71bb6a2577b'],
      '67cfcb7bf8c28c280603d7ba7a7831c5ee1ea040': ['0f05e24cc408cda9c573d3e76774e499d338b88d'],
      ...},
     {'43981b68b7a24544d4bc4f3094be7a12c9f0afe0': 'Key 43981b68b7a24544d4bc4f3094be7a12c9f0afe0 not found in /da8_data/basemaps/c2bFullV.3.tch'})



### Task 5: Go Async

The remote client also supports async API, which is useful when you are running multiple requests in parallel. APIs are similar to the sync ones, but with `await` in front of them.


```python
from woc.remote import WocMapsRemoteAsync, WocMapsRemote

woca = WocMapsRemoteAsync(
    base_url="https://woc.osslab-pku.org/api/",
)
[(m.name, m.version) for m in await woca.get_maps()]
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
     ('a2A', 'V0'),
     ('a2A', 'V3'),
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
     ...]




```python
# 1. get_values API

# woc.get_values('c2ta', 
#                woc.get_values('c2pc', '009d7b6da9c4419fe96ffd1fffb2ee61fa61532a')[0])

await woca.get_values('c2ta', 
               (await woca.get_values('c2pc', '009d7b6da9c4419fe96ffd1fffb2ee61fa61532a'))[0])
```




    ['1092637858', 'Maxim Konovalov <maxim@FreeBSD.org>']




```python
async for i in woca.iter_values("P2c", "user2589_minicms"):
    print(i)
```

    ['05cf84081b63cda822ee407e688269b494a642de', '086a622f0e24feb7853c520f965f04c7fc7e4861', '0ad5b0b392ed22cef866de5ae8504462183b0316', '104b8284ba6435a3c07eb5ce82f15cb0f956eda3', '1837bfa6553a9f272c5dcc1f6259ba17357cf8ed', '19ddf6dafb6014c954253bd022778051213ccd9a', '1d3038eab8cac1e8a9df187d411fbc0e4a317270', '1e971a073f40d74a1e72e07c682e1cba0bae159b', '1eda863abed481df83c680a6c31fad05719b166b', '27f6af62ff6facfb21a7fe33cddfc115f93cb75f', '2881cf0080f947beadbb7c240707de1b40af2747', '2c02c1f9b1a959c5228bf8cfad1a09fd5489b381', '3303b05caf2f9b51fc6323820fe9e04780c40e48', '335aeff4c90d4d31562a24b2648ed529ef664664', '3b0cbf364870cd35d9e41630387d97393fea2fa5', '3beec34c51d9ae5d60c7eb976bb03a95db235514', '3c57cd4791ac46ccb73cc22a50d9a4c77e5cd0a3', '3c59a5aca8ee3e201977558fe9f1ea5489d2b1b3', '3f68ba216c938e93aff1dc45b241511a0fa94e51', '43981b68b7a24544d4bc4f3094be7a12c9f0afe0', '4dffda766eba4f4edc31eb0b7691cc75d7775de0', '58898751944b69ffc04d148b0917473e2d5d5db8', '5b0afd26ed90f8b3352f4ac8a53da9f23597c42d', '63ff96cbb38687e68cb4fdd7e208aa70f66ba252', '66acf0a046a02b48e0b32052a17f1e240c2d7356', '67cfcb7bf8c28c280603d7ba7a7831c5ee1ea040', '6d031dc38204b9bb0ddf75f6f76ea28bc7e4d054', '710d45b6cfffb5d630b117572cf27fb1848fb5af', '78bd544cdb869b5b1f7280f6df2e856d1dbb8775', '7da8be92d11b33e913408438fa174dc524f1d9d9', '81494a6510c11dad3aabe14625b1644561f0af5f', '827f3a14d1edd48d36effbdb7cc5f44221df3a7a', '85787429380cb20b6a935e52c50f85f455790617', '8caff1690253f8a9596c9918819f24c9f79140ce', '8fb99ec51bccc6ea4828c6ea08cd0976b53e6edc', '995e6a997e3f841235487dac9c50f903d855aaa2', '9bd02434b834979bb69d0b752a403228f2e385e8', '9be4c4ec851fafc295c9e098a2e4741a8140f7be', 'a443e1e76c39c7b1ad6f38967a75df667b9fed57', 'aa779a8f11473abc461c61db917e2d3c3d2c2e5d', 'ab124ab4baa42cd9f554b7bb038e19d4e3647957', 'b35161cffea14767e66e75bece19b368815522d4', 'b66c430180f96fb1e7e821ec637f88e63c6c5aae', 'b782ea2936b97d0bfb3f2ed089b49b1a72414182', 'ba3659e841cb145050f4a36edb760be41e639d68', 'bb3701be55292fef1b0daa815199ff0886be540d', 'bde80c730ef2dc34e8c34291aae3174b78dd8cb0', 'd009acbf3b4e663fc101e4086e5cd06eb7e5e418', 'd04e0f15916c843aa1e4b8aeabb758999d22e390', 'd11431c3ef74770ac570a82b2fd9b19a690a4adc', 'd64156ef9a753c105958c34ae2518ad46d3dc6bb', 'd8b38d3798d277d1e15474f26aa8e6ae33ba2d67', 'd9a72b48e7bb3406022207039c3b9c1e22ea8955', 'de8985354c2af17bbc1263d8b3ae5e0f2330b540', 'dff7aa6c388b07f7fc9a171c1659d60df17c379f', 'dff95810cd0b99a6027cbb3f725b0116f6aa9f33', 'e25e7e06bcc63c7aca7d6ffa6f54fbc9f00b5da6', 'e38126dbca6572912013621d2aa9e6f7c50f36bc', 'e40c989e1e583ea5d32824c28231d594b10fce2b', 'e766916b4ab3ccd430ff3b0e55bcf2cae0772f91', 'e99e506f6214aec5fd0d52bf00f36c1df00de9be', 'eb081cc38858eab997921f9bc2bfb57596d5bdf8', 'f0d02fc17be5fdd57b969880fc0ea0f6fa96ba95', 'f2a7fcdc51450ab03cb364415f14e634fa69b62c', 'f2ac3a79ebc17c7f10814f5f13d3a17d8fc990c3', 'f5220ef868579d41c7fba0a66e9697d61626a4a7', 'fa695566bac8584045c4e95209aeb7c9e4adfe49', 'fe60de5ca98daae4a056c96544ed218aab28b0d2', 'fec2d855fb0086ab37e1a557a1e3531e187cfa0a']



```python
await woca.show_content("tree", "f1b66dcca490b5c4455af319bc961a34f69c72c2")
```




    [['100644', 'README.md', '05fe634ca4c8386349ac519f899145c75fff4169'],
     ['100644', 'course.pdf', 'dfcd0359bfb5140b096f69d5fad3c7066f101389']]


