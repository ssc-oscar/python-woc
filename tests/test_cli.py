import subprocess


def run_show_content(commit_hash, *args):
    result = subprocess.run(
        ["python3", "-m", "woc.show_content", *args, "-p", "./tests/test_profile.json"],
        capture_output=True,
        text=True,
        input=commit_hash,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def run_get_values(input_str, *args):
    result = subprocess.run(
        ["python3", "-m", "woc.get_values", *args, "-p", "./tests/test_profile.json"],
        capture_output=True,
        text=True,
        input=input_str,
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def test_cli_commit():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = (
        "e4af89166a17785c1d741b8b1d5775f3223f510f;"
        "f1b66dcca490b5c4455af319bc961a34f69c72c2;"
        "c19ff598808b181f1ab2383ff0214520cb3ec659;"
        "Audris Mockus <audris@utk.edu>;"
        "Audris Mockus <audris@utk.edu>;1410029988;1410029988"
    )
    actual_output = run_show_content(commit_hash, "commit")
    assert actual_output[1] == expected_output, actual_output


def test_cli_commit_1():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = (
        "e4af89166a17785c1d741b8b1d5775f3223f510f;1410029988;"
        "Audris Mockus <audris@utk.edu>"
    )
    actual_output = run_show_content(commit_hash, "commit", "1")
    assert actual_output[1] == expected_output, actual_output


def test_cli_commit_2():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = (
        "e4af89166a17785c1d741b8b1d5775f3223f510f;Audris Mockus <audris@utk.edu>;"
        "1410029988;-0400;News for Sep 5"
    )
    actual_output = run_show_content(commit_hash, "commit", "2")
    assert actual_output[1] == expected_output, actual_output


def test_cli_commit_3():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = """tree f1b66dcca490b5c4455af319bc961a34f69c72c2
parent c19ff598808b181f1ab2383ff0214520cb3ec659
author Audris Mockus <audris@utk.edu> 1410029988 -0400
committer Audris Mockus <audris@utk.edu> 1410029988 -0400

News for Sep 5"""
    actual_output = run_show_content(commit_hash, "commit", "3")
    assert actual_output[1] == expected_output, actual_output


def test_cli_commit_4():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = (
        "e4af89166a17785c1d741b8b1d5775f3223f510f;Audris Mockus <audris@utk.edu>"
    )
    actual_output = run_show_content(commit_hash, "commit", "4")
    assert actual_output[1] == expected_output, actual_output


def test_cli_commit_5():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = "e4af89166a17785c1d741b8b1d5775f3223f510f;c19ff598808b181f1ab2383ff0214520cb3ec659"
    actual_output = run_show_content(commit_hash, "commit", "5")
    assert actual_output[1] == expected_output, actual_output


def test_cli_commit_6():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output_end = "c19ff598808b181f1ab2383ff0214520cb3ec659"
    actual_output = run_show_content(commit_hash, "commit", "6")
    assert actual_output[1].endswith(expected_output_end), actual_output


def test_cli_commit_7():
    commit_hash = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output_end = "QHV0ay5lZHU+IDE0MTAwMjk5ODggLTA0MDAKCk5ld3MgZm9yIFNlcCA1\\n"
    actual_output = run_show_content(commit_hash, "commit", "7")
    assert actual_output[1].endswith(expected_output_end), actual_output


def test_cli_tree():
    tree_hash = "f1b66dcca490b5c4455af319bc961a34f69c72c2"
    expected_output = "100644;05fe634ca4c8386349ac519f899145c75fff4169;README.md\n100644;dfcd0359bfb5140b096f69d5fad3c7066f101389;course.pdf"
    actual_output = run_show_content(tree_hash, "tree")
    assert actual_output[1] == expected_output, actual_output


def test_cli_blob():
    blob_hash = "05fe634ca4c8386349ac519f899145c75fff4169"
    expected_output_start = '# Syllabus for "Fundamentals of Digital Archeology"\n\n## News\n\n* Assignment1 due Monday Sep 8 before 2:30PM'
    actual_output = run_show_content(blob_hash, "blob")
    assert actual_output[1].startswith(expected_output_start), actual_output


def test_cli_a2c():
    input_str = "Audris Mockus <audris@utk.edu>"
    expected_output_start = (
        "Audris Mockus <audris@utk.edu>;001ec7302de3b07f32669a1f1faed74585c8a8dc"
    )
    actual_output = run_get_values(input_str, "a2c")
    assert actual_output[1].startswith(expected_output_start), actual_output


def test_cli_a2f():
    input_str = "Audris Mockus <audris@utk.edu>"
    expected_output_start = (
        "Audris Mockus <audris@utk.edu>;.#analyze.sh;.README.md.swp;.Rhistory;.bowerrc"
    )
    actual_output = run_get_values(input_str, "a2f")
    assert actual_output[1].startswith(expected_output_start), actual_output


def test_cli_b2c():
    input_str = "05fe634ca4c8386349ac519f899145c75fff4169"
    expected_output = "05fe634ca4c8386349ac519f899145c75fff4169;e4af89166a17785c1d741b8b1d5775f3223f510f"
    actual_output = run_get_values(input_str, "b2c")
    assert actual_output[1] == expected_output, actual_output


def test_cli_c2b():
    input_str = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = "e4af89166a17785c1d741b8b1d5775f3223f510f;05fe634ca4c8386349ac519f899145c75fff4169"
    actual_output = run_get_values(input_str, "c2b")
    assert actual_output[1] == expected_output, actual_output


def test_cli_c2cc():  # expect error
    input_str = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    actual_output = run_get_values(input_str, "c2cc")
    assert actual_output[2].endswith("shard 0 not found at None"), actual_output


def test_cli_c2f():
    input_str = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = "e4af89166a17785c1d741b8b1d5775f3223f510f;README.md"
    assert run_get_values(input_str, "c2f")[1] == expected_output


def test_cli_c2p():
    input_str = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output_start = (
        "e4af89166a17785c1d741b8b1d5775f3223f510f;W4D3_news;chumekaboom_news"
    )
    actual_output = run_get_values(input_str, "c2p")
    assert actual_output[1].startswith(expected_output_start), actual_output


def test_cli_c2r():
    input_str = "e4af89166a17785c1d741b8b1d5775f3223f510f"
    expected_output = "e4af89166a17785c1d741b8b1d5775f3223f510f;9531fc286ef1f4753ca4be9a3bf76274b929cdeb;27"
    actual_output = run_get_values(input_str, "c2r")
    assert actual_output[1] == expected_output, actual_output


def test_cli_p2a():
    input_str = "ArtiiQ_PocketMine-MP"
    expected_output_start = (
        "ArtiiQ_PocketMine-MP;0929hitoshi <kimurahitoshi0929@yahoo.co.jp>;"
    )
    actual_output = run_get_values(input_str, "p2a")
    assert actual_output[1].startswith(expected_output_start), actual_output


def test_cli_p2c():
    input_str = "ArtiiQ_PocketMine-MP"
    expected_output_start = (
        "ArtiiQ_PocketMine-MP;0000000bab11354f9a759332065be5f066c3398f"
    )
    actual_output = run_get_values(input_str, "p2c")
    assert actual_output[1].startswith(expected_output_start), actual_output


def test_cli_b2tac():
    input_str = "05fe634ca4c8386349ac519f899145c75fff4169"
    expected_output_end = (
        "Audris Mockus <audris@utk.edu>;e4af89166a17785c1d741b8b1d5775f3223f510f"
    )
    actual_output = run_get_values(input_str, "b2tac")
    assert actual_output[1].endswith(expected_output_end), actual_output
