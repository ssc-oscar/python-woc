import os

import pytest

# Import the TCHashDB class
from woc.local import WocMapsLocal


@pytest.fixture
def woc():
    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc = WocMapsLocal(_test_pr)
    yield woc


def test_c2p(woc):
    res = woc.get_values("c2p", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    assert res[0] == "W4D3_news"


def test_c2dat(woc):
    res = woc.get_values("c2dat", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    assert res[0] == "1410029988"


def test_b2tac(woc):
    res = woc.get_values("b2tac", "05fe634ca4c8386349ac519f899145c75fff4169")
    assert res[0] == (
        "1410029988",
        "Audris Mockus <audris@utk.edu>",
        "e4af89166a17785c1d741b8b1d5775f3223f510f",
    )


def test_b2tac_vererr(woc):
    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc_r = WocMapsLocal(_test_pr, version="R")
    with pytest.raises(KeyError):
        woc_r.get_values("b2tac", "05fe634ca4c8386349ac519f899145c75fff4169")


def test_p2a(woc):
    res = woc.get_values("p2a", "ArtiiQ_PocketMine-MP")
    assert res[0] == "0929hitoshi <kimurahitoshi0929@yahoo.co.jp>"


def test_b2c(woc):
    res = woc.get_values("b2c", "05fe634ca4c8386349ac519f899145c75fff4169")
    assert res[0] == "e4af89166a17785c1d741b8b1d5775f3223f510f"


def test_b2c_large(woc):
    res = woc.get_values("b2c", "3f2eca18f1bc0f3117748e2cea9251e5182db2f7")
    assert res[0] == "00003a69db53b45a67f76632f33a93691da77197"


def test_a2c(woc):
    res = woc.get_values("a2c", "Audris Mockus <audris@utk.edu>")
    assert res[0] == "001ec7302de3b07f32669a1f1faed74585c8a8dc"


def test_c2cc_null_filename(woc):  # file name is null
    with pytest.raises(AssertionError):
        woc.get_values("c2cc", "e4af89166a17785c1d741b8b1d5775f3223f510f")


def test_a2f(woc):
    res = woc.get_values("a2f", "Audris Mockus <audris@utk.edu>")
    assert res[0] == ".#analyze.sh"


def test_c2f(woc):
    res = woc.get_values("c2f", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    assert res[0] == "README.md"


def test_c2b(woc):
    res = woc.get_values("c2b", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    assert res[0] == "05fe634ca4c8386349ac519f899145c75fff4169"


def test_p2c(woc):
    res = woc.get_values("p2c", "ArtiiQ_PocketMine-MP")
    assert res[0] == "0000000bab11354f9a759332065be5f066c3398f"


def test_f2a(woc):
    res = woc.get_values("f2a", "youtube-statistics-analysis.pdf")
    assert res[0] == "Audris Mockus <audris@utk.edu>"


def test_b2f(woc):
    res = woc.get_values("b2f", "05fe634ca4c8386349ac519f899145c75fff4169")
    assert res[0] == "README.md"


def test_c2r(woc):
    res = woc.get_values("c2r", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    assert res[0] == "9531fc286ef1f4753ca4be9a3bf76274b929cdeb"


def test_b2fa(woc):
    res = woc.get_values("b2fa", "05fe634ca4c8386349ac519f899145c75fff4169")
    assert res[0] == "1410029988"


def test_tree(woc):
    res = woc.show_content("tree", "f1b66dcca490b5c4455af319bc961a34f69c72c2")
    assert len(res) == 2


def test_commit(woc):
    res = woc.show_content("commit", "e4af89166a17785c1d741b8b1d5775f3223f510f")
    assert res[-1] == "News for Sep 5"


def test_blob_1(woc):
    res = woc.show_content("blob", "05fe634ca4c8386349ac519f899145c75fff4169")
    assert len(res) == 14194


def test_blob_2(woc):
    res = woc.show_content("blob", "46aaf071f1b859c5bf452733c2583c70d92cd0c8")
    assert len(res) == 1236


def test_count(woc):
    res = woc.count("blob")
    assert res == 2
    res = woc.count("tree")
    assert res == 12
    res = woc.count("commit")
    assert res == 7


def test_all_keys(woc):
    res = list(woc.all_keys("blob"))
    assert len(res) == 2
    assert all(isinstance(r, bytes) for r in res)
    res = list(woc.all_keys("tree"))
    assert len(res) == 12
    assert all(isinstance(r, bytes) for r in res)
    res = list(woc.all_keys("commit"))
    assert len(res) == 7
    assert all(isinstance(r, bytes) for r in res)


def test_version(woc):
    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc_u = WocMapsLocal(_test_pr, version="U")
    assert {m.name for m in woc_u.maps} == {"b2fa", "c2p", "c2dat", "b2tac"}
    woc_r = WocMapsLocal(_test_pr, version=["R"])
    assert len(woc_u.maps) + len(woc_r.maps) == len(woc.maps)


def test_exclude_larges(woc):
    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc_nolarge = WocMapsLocal(_test_pr, on_large="ignore")
    with pytest.raises(KeyError):
        woc_nolarge.get_values("b2c", "3f2eca18f1bc0f3117748e2cea9251e5182db2f7")
