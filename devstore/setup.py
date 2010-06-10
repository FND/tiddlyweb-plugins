import os

try: # development environment
	import mangler
except ImportError:
	pass

from setuptools import setup, find_packages


VERSION = "0.7.6" # N.B.: duplicate of tiddlywebplugins.devstore


setup(
	name = "tiddlywebplugins.devstore",
	version = VERSION,
	url = "http://pypi.python.org/pypi/tiddlywebplugins.devstore",
	description = "TiddlyWeb store implementation supporting client-side development",
	long_description = file(os.path.join(os.path.dirname(__file__), "README")).read(),
	platforms = "Posix; MacOS X; Windows",
	author = "FND",
	author_email = "FNDo@gmx.net",
	scripts = ['twinstance_dev'],
	namespace_packages = ["tiddlywebplugins"],
	packages = find_packages(exclude=["test"]),
	install_requires = [
		"setuptools",
		"tiddlywebwiki",
		"tiddlywebplugins.twimport"
	]
)
