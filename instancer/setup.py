import os

from setuptools import setup, find_packages


VERSION = "0.1"


setup(
        namespace_packages = ["tiddlywebplugins"],
        name = "tiddlywebplugins.instancer",
        version = VERSION,
        url = "http://pypi.python.org/pypi/tiddlywebplugins.instancer",
        description = "A TiddlyWeb plugin to simplify instance management for verticals.",
        long_description = file(os.path.join(os.path.dirname(__file__), "README")).read(),
        platforms = "Posix; MacOS X; Windows",
        author = "FND",
        author_email = "FNDo@gmx.net",
        packages = find_packages(exclude=["test", "twp"]),
        install_requires = ["setuptools", "tiddlyweb"]
)
