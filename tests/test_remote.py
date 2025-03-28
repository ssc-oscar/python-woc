import os

import pytest

from woc.remote import WocMapsRemote, WocMapsRemoteAsync

WOC_BASE_URL = os.getenv("WOC_BASE_URL") or "https://wocapi-preview.osslab-pku.org"


@pytest.fixture
def woca():
    return WocMapsRemoteAsync(base_url=WOC_BASE_URL)


@pytest.fixture
def woc():
    return WocMapsRemote(base_url=WOC_BASE_URL)


@pytest.mark.asyncio
async def test_get_maps_async(woca):
    maps = await woca.get_maps()
    assert len(maps) > 0


@pytest.mark.asyncio
async def test_get_values_async(woca):
    values = await woca.get_values("P2c", "user2589_minicms")
    assert len(values) > 0


@pytest.mark.asyncio
async def test_iter_values_async(woca):
    res = []
    async for i in woca.iter_values("P2c", "user2589_minicms"):
        res.append(i)
    assert len(res) > 0


@pytest.mark.asyncio
async def test_get_objects_async(woca):
    objects = await woca.get_objects()
    assert len(objects) > 0


@pytest.mark.asyncio
async def test_get_values_many_async(woca):
    values = await woca.get_values_many("P2c", ["user2589_minicms"] * 12)
    assert len(values) > 0


@pytest.mark.asyncio
async def test_get_values_many_progress_async(woca):
    values = await woca.get_values_many("P2c", ["user2589_minicms"] * 23, progress=True)
    assert len(values) > 0


@pytest.mark.asyncio
async def test_show_content_many_async(woca):
    values = await woca.show_content_many(
        "tree", ["f1b66dcca490b5c4455af319bc961a34f69c72c2"] * 12
    )
    assert len(values) > 0


@pytest.mark.asyncio
async def test_count_map_async(woca):
    count = await woca.count("P2c")
    assert count > 0


@pytest.mark.asyncio
async def test_count_object_async(woca):
    count = await woca.count("commit")
    assert count > 0


@pytest.mark.asyncio
async def test_404_async(woca):
    with pytest.raises(KeyError):
        await woca.get_values("P2c", "user2589_minicms" * 2)


@pytest.mark.asyncio
async def test_400_async(woca):
    with pytest.raises(KeyError):
        await woca.get_values("c2c2cccc", "user2589_minicms")


def test_get_maps(woc):
    maps = woc.maps
    assert len([m.name for m in maps]) > 0


def test_get_objects(woc):
    objects = woc.objects
    assert len([o.name for o in objects]) > 0


def test_get_values(woc):
    values = woc.get_values("P2c", "user2589_minicms")
    assert len(values) > 0


def test_iter_values(woc):
    res = []
    for i in woc.iter_values("P2c", "user2589_minicms"):
        res.append(i)
    assert len(res) > 0


def test_show_content(woc):
    content = woc.show_content("tree", "f1b66dcca490b5c4455af319bc961a34f69c72c2")
    assert len(content) > 0


def test_show_content_many(woc):
    content = woc.show_content_many(
        "tree", ["f1b66dcca490b5c4455af319bc961a34f69c72c2"] * 12
    )
    assert len(content) > 0


def test_count(woc):
    count = woc.count("P2c")
    assert count > 0
