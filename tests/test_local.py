import multiprocessing
import os

import pytest

# Import the TCHashDB class
from woc.local import WocMapsLocal, decode_str


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


def test_tag(woc):
    res = woc.show_content("tag", "08af22b7de836a5fef0f9947a5f0894d371742de")
    assert res[0] == "3366f276c63b17a3d78865e12f6d94595f87bb18"


def test_c2tag(woc):
    res = woc.get_values("c2tag", "fcadcb9366d4a011039e384affa10961e99cf2c4")
    assert res[0] == "eccube-2.11.1"


def test_commit_tch(woc):
    res = woc.get_values("commit.tch", "898d5a21241aaf16acf92566aa34103d06cf2ac6")
    assert res[0][0] == "e5798457aebae7c84eff7b80b50c3a938cc4cb63"


def test_tree_tch(woc):
    res = woc.get_values("tree.tch", "51968a7a4e67fd2696ffd5ccc041560a4d804f5d")
    assert res[0][0] == (
        "100644",
        "Dockerfile",
        "9abdd1032c7cc49568d22bf45673f30ddb159efc",
    )


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


def test_bad_keys():
    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc_err = WocMapsLocal(_test_pr, on_bad="error")
    with pytest.raises(KeyError):
        woc_err.get_values("p", "bitzhoumy_helloworld")
    with pytest.raises(KeyError):
        woc_err.get_values("c", "3f631f976149d8702d0b1496df7b98f16a9357ed")


_FORK_WOC = None


def _fork_get_values_worker(queue):
    global _FORK_WOC
    queue.put(_FORK_WOC.get_values("c2p", "e4af89166a17785c1d741b8b1d5775f3223f510f")[0])


def test_get_values_after_fork():
    try:
        ctx = multiprocessing.get_context("fork")
    except ValueError:
        pytest.skip("fork start method not available")

    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc = WocMapsLocal(_test_pr)
    assert (
        woc.get_values("c2p", "e4af89166a17785c1d741b8b1d5775f3223f510f")[0]
        == "W4D3_news"
    )

    global _FORK_WOC
    _FORK_WOC = woc

    queue = ctx.Queue()
    proc = ctx.Process(target=_fork_get_values_worker, args=(queue,))
    proc.start()

    value = queue.get(timeout=5)
    proc.join(timeout=5)

    assert proc.exitcode == 0
    assert value == "W4D3_news"

    _FORK_WOC = None


def test_decode_str():
    assert decode_str("新建文件夹".encode("utf-8")) == "新建文件夹"
    assert (
        decode_str("复件 (1) - 代码文件.rar".encode("gb2312"))
        == "复件 (1) - 代码文件.rar"
    )
    assert (
        decode_str("深层路径/源码/测试/最终版_v2.c".encode("gb18030"))
        == "深层路径/源码/测试/最终版_v2.c"
    )
    assert decode_str("新しいフォルダー".encode("shift_jis")) == "新しいフォルダー"
    assert (
        decode_str("デスクトップ/ソースコード.txt".encode("shift_jis"))
        == "デスクトップ/ソースコード.txt"
    )
    assert decode_str("新增資料夾".encode("big5")) == "新增資料夾"
    assert decode_str("專案備份/未命名.bmp".encode("big5")) == "專案備份/未命名.bmp"
    assert decode_str("공지사항.hwp".encode("cp949")) == "공지사항.hwp"
    assert decode_str("Новая папка".encode("cp1251")) == "Новая папка"
    assert (
        decode_str("C:/Program Files/Разное/readme.txt".encode("cp1251"))
        == "C:/Program Files/Разное/readme.txt"
    )
    assert (
        decode_str("Nouveau dossier/Crédit Agricole.pdf".encode("cp1252"))
        == "Nouveau dossier/Crédit Agricole.pdf"
    )
    assert decode_str("München_Straße.jpg".encode("cp1252")) == "München_Straße.jpg"
    assert decode_str("Price_€500.txt".encode("cp1252")) == "Price_€500.txt"
    assert (
        decode_str(b"css/\xd0\xc2\xbd\xa8\xce\xc4\xbc\xfe\xbc\xd0/images")
        == "css/新建文件夹/images"
    )
