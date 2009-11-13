import os

try: # development environment
	import mangler
except ImportError:
	pass

from setuptools import setup, find_packages

from tiddlywebplugins.instancer import __version__


setup(
	name = "tiddlywebplugins.instancer",
	version = __version__,
	url = "http://pypi.python.org/pypi/tiddlywebplugins.instancer",
	description = "TiddlyWeb plugin to simplify instance management for verticals",
	long_description = file(os.path.join(os.path.dirname(__file__), "README")).read(),
	platforms = "Posix; MacOS X; Windows",
	author = "FND",
	author_email = "FNDo@gmx.net",
	namespace_packages = ["tiddlywebplugins"],
	packages = find_packages(exclude=["test"]),
	install_requires = ["setuptools", "tiddlyweb", "tiddlywebplugins.utils"] # XXX: include optional tiddlywebwiki?
)
