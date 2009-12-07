import os

from setuptools import setup, find_packages

try: # development environment
	import mangler
	from tiddlywebplugins.instancer import __version__ as VERSION
except ImportError:
	VERSION = None


setup(
	name = "tiddlywebplugins.instancer",
	version = VERSION,
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
