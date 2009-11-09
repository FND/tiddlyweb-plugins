import os

from setuptools import setup, find_packages


VERSION = "0.1"


setup(
        namespace_packages = ["tiddlywebplugins"],
        name = "tiddlywebplugins.instancer",
        version = VERSION,
        description = "A TiddlyWeb plugin to simplify instance management for verticals.",
        long_description = file(os.path.join(os.path.dirname(__file__), "README")).read(),
        author = "FND",
        url = "http://pypi.python.org/pypi/tiddlywebplugins.instancer",
        packages = find_packages(exclude=["test", "twp"]),
        platforms = "Posix; MacOS X; Windows",
        install_requires = ["setuptools", "tiddlyweb"],
)
