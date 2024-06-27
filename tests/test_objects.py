import os

import pytest

# Import the TCHashDB class
from woc.local import WocMapsLocal
from woc.objects import *


@pytest.fixture
def woc():
    _test_pr = os.path.join(os.path.dirname(__file__), "test_profile.json")
    woc = WocMapsLocal(_test_pr)
    init_woc_objects(woc)
    yield woc


def test_equal(woc):
    assert Author("1") == Author("1")
    assert Blob("05fe634ca4c8386349ac519f899145c75fff4169") == Blob(
        "05fe634ca4c8386349ac519f899145c75fff4169"
    )
    assert Author("1") != Project("2")


def test_author_commits(woc):
    author = Author("Audris Mockus <audris@utk.edu>")
    commits = author.commits
    assert all(isinstance(c, Commit) for c in commits)
    assert commits[0].key == "001ec7302de3b07f32669a1f1faed74585c8a8dc"


def test_author_files(woc):
    author = Author("Audris Mockus <audris@utk.edu>")
    files = author.files
    assert all(isinstance(f, File) for f in files)
    assert files[0].key == ".#analyze.sh"


def test_author_name_email(woc):
    author = Author("Audris Mockus <audris@utk.edu>")
    assert author.name == "Audris Mockus"
    assert author.email == "audris@utk.edu"


def test_blob_data(woc):
    blob = Blob("05fe634ca4c8386349ac519f899145c75fff4169")
    res = blob.data
    assert len(res) == 14194


def test_blob_commits(woc):
    blob = Blob("05fe634ca4c8386349ac519f899145c75fff4169")
    commits = blob.commits
    assert all(isinstance(c, Commit) for c in commits)
    assert commits[0].key == "e4af89166a17785c1d741b8b1d5775f3223f510f"


def test_blob_commits_large(woc):
    blob = Blob("3f2eca18f1bc0f3117748e2cea9251e5182db2f7")
    commits = blob.commits
    assert all(isinstance(c, Commit) for c in commits)
    assert commits[0].key == "00003a69db53b45a67f76632f33a93691da77197"


def test_blob_first_author(woc):
    blob = Blob("05fe634ca4c8386349ac519f899145c75fff4169")
    date, author, commit = blob.first_author
    assert isinstance(date, datetime)
    assert isinstance(author, Author)
    assert isinstance(commit, Commit)
    assert date.timestamp() == 1410029988
    assert date.tzinfo is None  # naive datetime
    assert author.key == "Audris Mockus <audris@utk.edu>"
    assert commit.key == "e4af89166a17785c1d741b8b1d5775f3223f510f"


def test_blob_time_author_commits(woc):
    blob = Blob("05fe634ca4c8386349ac519f899145c75fff4169")
    date, author, commit = blob.time_author_commits[0]
    assert isinstance(date, datetime)
    assert isinstance(author, Author)
    assert isinstance(commit, Commit)
    assert date.timestamp() == 1410029988
    assert date.tzinfo is None  # naive datetime
    assert author.key == "Audris Mockus <audris@utk.edu>"
    assert commit.key == "e4af89166a17785c1d741b8b1d5775f3223f510f"


def test_blob_files(woc):
    blob = Blob("05fe634ca4c8386349ac519f899145c75fff4169")
    files = blob.files
    assert all(isinstance(f, File) for f in files)
    assert files[0].key == "README.md"


def test_commit_author(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    author = commit.author
    assert isinstance(author, Author)
    assert author.key == "Audris Mockus <audris@utk.edu>"


def test_commit_authored_at(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    authored_at = commit.authored_at
    assert isinstance(authored_at, datetime)
    assert authored_at.timestamp() == 1410029988
    assert authored_at.tzinfo is not None  # aware datetime


def test_commit_committer(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    committer = commit.committer
    assert isinstance(committer, Author)
    assert committer.key == "Audris Mockus <audris@utk.edu>"


def test_commit_committed_at(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    committed_at = commit.committed_at
    assert isinstance(committed_at, datetime)
    assert committed_at.timestamp() == 1410029988
    assert committed_at.tzinfo is not None  # aware datetime


def test_commit_full_message(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    full_message = commit.full_message
    assert full_message == "News for Sep 5"


def test_commit_message(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    message = commit.message
    assert message == "News for Sep 5"


def test_commit_tree(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    tree = commit.tree
    assert isinstance(tree, Tree)
    assert tree.key == "f1b66dcca490b5c4455af319bc961a34f69c72c2"


def test_commit_parents(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    parents = commit.parents
    assert all(isinstance(p, Commit) for p in parents)
    assert parents[0].key == "c19ff598808b181f1ab2383ff0214520cb3ec659"


def test_commit_projects(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    projects = commit.projects
    assert all(isinstance(p, Project) for p in projects)
    assert projects[0].key == "W4D3_news"


def test_commit_children_null_filename(woc):
    with pytest.raises(AssertionError):
        commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
        children = commit.children


def test_commit_files(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    files = commit.files
    assert all(isinstance(f, File) for f in files)
    assert files[0].key == "README.md"


def test_commit_blobs(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    blobs = commit.blobs
    assert blobs[0].key == "05fe634ca4c8386349ac519f899145c75fff4169"
    assert all(isinstance(b, Blob) for b in blobs)


def test_commit_time_author(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    time_author = commit.time_author
    assert isinstance(time_author[0], datetime)
    assert isinstance(time_author[1], Author)
    assert time_author[0].timestamp() == 1410029988
    assert time_author[0].tzinfo is None  # naive datetime


def test_commit_root(woc):
    commit = Commit("e4af89166a17785c1d741b8b1d5775f3223f510f")
    root, distance = commit.root
    assert isinstance(root, Commit)
    assert root.key == "9531fc286ef1f4753ca4be9a3bf76274b929cdeb"
    assert distance == 27


def test_file_authors(woc):
    file = File("youtube-statistics-analysis.pdf")
    authors = file.authors
    assert all(isinstance(a, Author) for a in authors)
    assert authors[0].key == "Audris Mockus <audris@utk.edu>"


def test_tree_files(woc):
    tree = Tree("f1b66dcca490b5c4455af319bc961a34f69c72c2")
    files = tree.files
    assert all(isinstance(f, File) for f in files)
    assert set(files) == {File("README.md"), File("course.pdf")}, str(files)


def test_tree_blobs(woc):
    tree = Tree("f1b66dcca490b5c4455af319bc961a34f69c72c2")
    blobs = tree.blobs
    assert all(isinstance(b, Blob) for b in blobs)
    assert Blob("05fe634ca4c8386349ac519f899145c75fff4169") in blobs


def test_tree_traverse(woc):
    tree = Tree("706aa4dedb560358bff21c3120a0b09532d3484d")
    traverse = list(tree.traverse())
    assert all(isinstance(t[0], File) for t in traverse)
    assert all(isinstance(t[1], Blob) for t in traverse)


def test_project_authors(woc):
    project = Project("ArtiiQ_PocketMine-MP")
    authors = project.authors
    assert all(isinstance(a, Author) for a in authors)
    assert authors[0].key == "0929hitoshi <kimurahitoshi0929@yahoo.co.jp>"


def test_project_commits(woc):
    project = Project("ArtiiQ_PocketMine-MP")
    commits = project.commits
    assert all(isinstance(c, Commit) for c in commits)
    assert commits[0].key == "0000000bab11354f9a759332065be5f066c3398f"


def test_project_url(woc):
    project = Project("ArtiiQ_PocketMine-MP")
    assert project.url == "https://github.com/ArtiiQ/PocketMine-MP"
    project = Project(
        "sourceforge.net_peazip"
    )  # <- How does sourceforge repos looks like in woc?
    assert project.url == "https://git.code.sf.net/p/peazip"
    project = Project("gitlab.com_openRGB_openRGB")
    assert project.url == "https://gitlab.com/openRGB/openRGB"
    project = Project("chromium.googlesource.com_chromiumos_platform/factory")
    assert project.url == "https://chromium.googlesource.com/chromiumos/platform/factory"
    project = Project("greicekcgm_greice_kelli_cristan_goncalves_mota_jamstackalura")
    assert (
        project.url
        == "https://github.com/greicekcgm/greice_kelli_cristan_goncalves_mota_jamstackalura"
    )


def test_project_head(woc):
    project = Project("woc-hack_thebridge")
    head = project.head
    assert isinstance(head, Commit)
    assert head.key == "f249b14a111279faa8d65c29ecf46bb6ce59a139"


def test_project_tail(woc):
    project = Project("woc-hack_thebridge")
    tail = project.tail
    assert isinstance(tail, Commit)
    assert tail.key == "ae6e15fa4d8d4d454977ddbb4e97e922ddecebf7"


def test_project_earliest(woc):
    project = Project("woc-hack_thebridge")
    earliest = project.earliest_commit
    assert isinstance(earliest, Commit)
    assert earliest.key == "ae6e15fa4d8d4d454977ddbb4e97e922ddecebf7"


def test_project_latest(woc):
    project = Project("woc-hack_thebridge")
    latest = project.latest_commit
    assert isinstance(latest, Commit)
    assert latest.key == "f249b14a111279faa8d65c29ecf46bb6ce59a139"


def test_project_walk(woc):
    project = Project("woc-hack_thebridge")
    commits = list(project.commits_fp())
    assert all(isinstance(c, Commit) for c in commits)
    assert len(commits) == 6


def test_commit_compare(woc):
    c1 = Commit("91f4da4c173e41ffbf0d9ecbe2f07f3a3296933c")
    c2 = Commit("ae6e15fa4d8d4d454977ddbb4e97e922ddecebf7")

    # We can't test fuzz matching because blob storage is broken :(
    diff = list(c1.compare(c2, threshold=1))
    modified_files = {f[0].key for f in diff if f[0] is not None} | {
        f[1].key for f in diff if f[1] is not None
    }
    assert all(len(d) == 4 for d in diff)
    assert all(isinstance(d[0], File) for d in diff if d[0] is not None)
    assert all(isinstance(d[1], File) for d in diff if d[1] is not None)
    assert all(isinstance(d[2], Blob) for d in diff if d[2] is not None)
    assert all(isinstance(d[3], Blob) for d in diff if d[3] is not None)
    assert modified_files == {
        "README.md",
        "woc_service/requirements.txt",
        "woc_service/app.py",
        "woc_service/static/.keep",
        "woc_service/oscar.py",
    }
