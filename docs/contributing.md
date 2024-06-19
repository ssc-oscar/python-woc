
## How to commit

We follow the standard "fork-and-pull" Git workflow. All the development is done on feature branches, which are then merged to `master` via pull requests. Pull requires are unit tested and linted automatically.

To generate release notes, we use [conventional commits](https://www.conventionalcommits.org),
a convention to commit messages. In a nutshell, it means commit messages should
be prefixed with one of:

- **fix:** in case the change fixes a problem without changing any interfaces.
  Example commit message: `fix: missing clickhouse-driver dependency (closes #123)`.
- **feat:** the change implements a new feature, without affecting existing
  interfaces. Example: `feat: implement author timeline`.
- other prefixes, e.g. `chore:`, `refactor:`, `docs:`, `test:`, `ci:`, etc.
  - these will not be included in release notes and will not trigger a new
  release without new features or fixes added, unless contain breaking changes
  (see below).

In case of breaking changes, commit message should include an exclamation mark
before the semicolon, or contain **BREAKING CHANGE** in the footer, e.g.:

    `feat!: drop support for deprectated parameters`

Commit hooks will reject commits that do not follow the convention, so you have no choice but to follow the rules 😈

## Setup development environment

### Setup Poetry

To make sure everyone is on the same page, we use [poetry](https://python-poetry.org)
to manage dependencies and virtual environments. 
If you don't have it installed yet, please follow the [installation guide](https://python-poetry.org/docs/#installation).

After installing poetry, create an virtual environment and install all dependencies:

```bash
poetry shell       # activate the virtual environment
poetry install     # install all dependencies
```

The `poetry install` command builds `python-woc` from source as well.

### Install pre-commit hooks

Pre-commit hooks ensure that all code is formatted, linted, and tested before pushed to GitHub. 
This "fail fast, fail early" approach saves time and effort for all of us.


```bash
# install linter and unit tests to pre-commit hooks
pre-commit install 
# install the conventional commits checker
pre-commit install --hook-type commit-msg  
```

## About Cython

(Notes from the original maintainer, @moo-ack)

The reason to use Cython was primarily Python 3 support. WoC data is stored
in tokyocabinet (.tch) files, note natively supported by Python.
`libtokyocabinet` binding, `python-tokyocabinet`, is a C extension supporting
Python 2 only, and lack of development activity suggests updating it for Py 3
is hardly considered. So, our options to interface `libtokyocabinet` were:

- cffi (C Foreign Functions Interface) - perhaps, the simplest option,
  but it does not support conditional definitions (`#IFDEF`), that are
  actively used in tokyocabinet headers
- C extension, adapting existing `python-tokyocabinet` code for Python 3.
  It is rather hard to support and even harder to debug; a single
  attempt was scrapped after making a silently failing extension.
- [SWIG](http://swig.org)(and its successor, [CLIF](https://github.com/google/clif)),
  a Google project to generate C/C++ library bindings
  for pretty much any language. Since this library provides 1:1 interface
  to the library methods, Python clients had to be aware of the returned
  C structures used by libtokyocabinet, which too inconvenient.
- Cython, a weird mix of Python and C. It allows writing Python interfaces,
  while simultaneously using C functions. This makes it the ideal option
  for our purposes, providing a Python `.tch` file handler working
  with `libtokyocabinet` C structures under the hood.

Cython came a clear winner in this comparison, also helping to speed up
some utility functions along the way (e.g. `fnvhash`, a pure Python version
of which was previously used).

## Compile changes to Cython code

Cython code is not interpreted; it needs to be compiled to C and then to a shared object file. If you made any changes to `.pyx` or `.pxd` files, you need to recompile:

```bash
python3 setup.py
```

Cython requires a functioning GNU toolchain. And sometimes ld complains it can not find `-lbz2`, and you need to install `bzip2-devel` package on CentOS or `libbz2-dev` on Ubuntu.

## Lint

We use [ruff](https://github.com/astral-sh/ruff) as the one and only linter and formatter. Being in Rust, it is blazingly fast and perfect for commit hooks and CI. The pre-commit hooks already include the following:

```bash
ruff format        # format all Python code
ruff check         # lint all Python code
ruff check --fix   # fix all linting issues
```

But ruff's fix feature is very cautious: sometimes it refuse to perform "unsafe" changes, and yields an error when you commit. In this case, we recommend installing the [ruff VSCode integration](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff), double check the suggested changes, and apply them manually.

## Test

### Run tests

python-woc use pytest to run unit tests, and pytest-cov to check coverage. To run tests:

```bash
pytest              # run all unit tests
pytest -k test_name # run a specific test
pytest --cov        # run all tests and check coverage
```

### Add a new test case

Test cases are located at `tests/` directory. To add a new test case, create a new file with the name `test_*.py`, like the following:

```python
# tests/test_my_new_feature.py
def test_my_new_feature():
    assert 1 == 1
```

### Add a new fixture

Some may claim that the binary fixtures is good enough for testing, but we prefer to incorporate generation scripts into the test suite. To add a new fixture, add a line to `tests/fixtures/create_fixtures.py`:

```python
cp.copy_content("tree", "51968a7a4e67fd2696ffd5ccc041560a4d804f5d")
```

Run `create_fixtures.py` on a server with WoC datasets, generate a profile at `./wocprofile.json`, and the following at the project root:

```bash
PYTHONPATH=. python3 tests/fixtures/create_fixtures.py
```

## Manage dependencies

Managing dependencies is not hard with poetry. To add a new dependency, run:

```bash
poetry add package_name  # add a new dependency
```

Sometimes tasks are easier to perform to edit the manifest file directly, e.g. add a new dependency to a specific group. You need to update the lockfile manually or poetry gets angry on install:

```bash
nano pyproject.toml      # add a new dependency manually
poetry lock --no-update  # update the lock file
```

Poetry is heavy to install and setup. To make it easier for manual installation, we keep a `requirements.txt` file. You will need to update it after modifying dependencies:

```bash
poetry check --lock
poetry export -f requirements.txt --with build --output requirements.txt
```

## Test GitHub actions locally

It's always a good idea to test your code before commit to avoid fixups polluting the commit history. You can run the GitHub actions locally with [act](https://github.com/nektos/act) to see if it works as expected:

```bash
act -j 'test' -s CODECOV_TOKEN  # run unit tests
act -j 'build-and-publish' --artifact-server-path build  # run the wheel builder
act -j 'docs' -s GITHUB_TOKEN  # run the documentation generator
```

## Build wheels

Actually the easiest way to build manylinux wheels is to run the GitHub action locally, with [act](https://github.com/nektos/act). (Note that write permission to docker socket is required) You will get the exact same wheels as the CI produces:

```bash
act -j 'build-wheel' --artifact-server-path build
cd build/1/wheels/
# Somehow artifacts are gzipped, and we need to unzip them
for f in *.gz__; do mv "$f" "${f%__}"; gzip -d "${f%__}"; done
# move them to dist/
mv *.whl ../../../dist/
```

Note that even `poetry build` does produce manylinux wheels, its compatibility level is not guaranteed. To ensure the wheels are compatible with CentOS 7, we fix the level to manylinux2014.

## Bump version

You don't have to, and please do not change version number manually. Use poetry to bump the version number:

```bash
poetry version patch  # or minor, or major, or pre-release
```

For the full usage, please refer to the [poetry documentation](https://python-poetry.org/docs/cli/#version).

## Add new mappings to python-woc

### `woc.get_values`

We don't hard code how to encode and decode each one of the mappings. Instead, we follow the practice of the original [World of Code perl driver](https://github.com/ssc-oscar/lookup/blob/7289885/getValues.perl#L34) and define the following datatypes:

```json
{
  "h": "hex",
  "s": "str",
  "cs": "[compressed]str",
  "sh": "str_hex",
  "hhwww": "hex_hex_url",
  "r": "hex_berint",
  "cs3": "[compressed]str_str_str"
}
```

`woc.detect` should be able to recognize the new mappings if they follow the current naming scheme. To get `get_values` working, you may add a new line to `woc/detect.py` and regenerate the profile, or modify the following field in `wocprofile.json`:

```json
"dtypes": [
  "h",  // Input dtype
  "cs3"  // Output dtype
]
```

### `woc.show_content`

`woc.show_content` is a bit tricky, and we have to implement the encoders and decoders separately. To add another git object, please refer to existing implementations in `woc/local.pyx`.

### `woc.objects`

The implementation of the object API is in pure python, at `woc/objects.py`.
 A new object class need to be a subclass of one of the following:

- `_GitObject`: A hash-indexed Git object, e.g. commit, tree, blob
- `_NamedObject`: A named object indexed by its fnv hash, e.g. author, project