import os

from setuptools import setup, find_packages


VERSION = "0.6.0" # N.B.: duplicate of tiddlywebplugins.instancer.__init__


setup(
	name = "tiddlywebplugins.instancer",
	version = VERSION,
	url = "http://pypi.python.org/pypi/tiddlywebplugins.instancer",
	description = "utilities to simplify instance management for TiddlyWeb verticals",
	long_description = file(os.path.join(os.path.dirname(__file__), "README")).read(),
	platforms = "Posix; MacOS X; Windows",
	author = "FND",
	author_email = "FNDo@gmx.net",
	namespace_packages = ["tiddlywebplugins"],
	packages = find_packages(exclude=["test"]),
	install_requires = ["setuptools", "tiddlyweb>=0.9.83", "tiddlywebplugins.utils"]
)
