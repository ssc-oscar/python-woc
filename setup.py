import os
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize

ROOT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_ROOT = os.path.join(ROOT, "woc")
TCH_ROOT = os.path.join(ROOT, "lib")
PACKAGES = find_packages(where=PACKAGE_ROOT)

ext_modules = [
    Extension(
        'woc.local', 
        libraries=['bz2', 'z'], 
        include_dirs=['lib'],
        sources=[
            os.path.join(PACKAGE_ROOT, 'local.pyx'),
        ], 
        extra_compile_args=['-std=gnu11']
    ),
    Extension(
        'woc.tch', 
        libraries=['bz2', 'z'], 
        include_dirs=['lib'],
        sources=[
            os.path.join(PACKAGE_ROOT, 'tch.pyx'),
            os.path.join(TCH_ROOT, 'tchdb.c'), 
            os.path.join(TCH_ROOT, 'myconf.c'),
            os.path.join(TCH_ROOT, 'tcutil.c'),
            os.path.join(TCH_ROOT, 'md5.c')
        ], 
        extra_compile_args=['-std=gnu11']
    ),
]

setup(
    name="python-woc",
    ext_modules=cythonize(ext_modules),
    packages=PACKAGES,
    package_data={"": ["*.pyx", "*.pxd", "*.pxi"]},
    include_package_data=True,
)