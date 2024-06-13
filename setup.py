import os

from Cython.Build import cythonize

# Thanks to @tryptofame for proposing an updated snippet
from Cython.Compiler.Options import get_directive_defaults
from setuptools import Extension, find_packages, setup

directive_defaults = get_directive_defaults()

directive_defaults["linetrace"] = True
directive_defaults["binding"] = True

ROOT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = os.path.join(ROOT, "woc")
TCH_ROOT = os.path.join(ROOT, "lib")
PACKAGES = find_packages(where=PACKAGE_ROOT)

ext_modules = [
    Extension(
        "woc.local",
        libraries=["bz2", "z"],
        include_dirs=["lib"],
        sources=[
            os.path.join(PACKAGE_ROOT, "local.pyx"),
        ],
        extra_compile_args=["-std=gnu11"],
        define_macros=[("CYTHON_TRACE", "1")],
    ),
    Extension(
        "woc.tch",
        libraries=["bz2", "z"],
        include_dirs=["lib"],
        sources=[
            os.path.join(PACKAGE_ROOT, "tch.pyx"),
            os.path.join(TCH_ROOT, "tchdb.c"),
            os.path.join(TCH_ROOT, "myconf.c"),
            os.path.join(TCH_ROOT, "tcutil.c"),
            os.path.join(TCH_ROOT, "md5.c"),
        ],
        extra_compile_args=["-std=gnu11"],
        define_macros=[("CYTHON_TRACE", "1")],
    ),
]

_default_args = ["build_ext", "--inplace"]
# if no arguments are provided, use the default ones
if len(os.sys.argv) == 1:
    os.sys.argv.extend(_default_args)

setup(
    name="python-woc",
    ext_modules=cythonize(ext_modules, emit_linenums=True),
    packages=PACKAGES,
    package_data={"": ["*.pyx", "*.pxd", "*.pyi"]},
    include_package_data=True,
)
