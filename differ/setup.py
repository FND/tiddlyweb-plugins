AUTHOR = "FND"
AUTHOR_EMAIL = "FNDo@gmx.net"
NAME = "tiddlywebplugins.differ"
DESCRIPTION = "TiddlyWeb plugin to compare tiddler revisions"
VERSION = "0.6.1"


import os

from setuptools import setup, find_packages


setup(
	namespace_packages = ["tiddlywebplugins"],
	name = NAME,
	version = VERSION,
	description = DESCRIPTION,
	long_description = open(os.path.join(os.path.dirname(__file__), "README")).read(),
	author = AUTHOR,
	url = "http://pypi.python.org/pypi/%s" % NAME,
	packages = find_packages(exclude="test"),
	author_email = AUTHOR_EMAIL,
	platforms = "Posix; MacOS X; Windows",
	install_requires = ["setuptools", "tiddlyweb"],
	zip_safe = False
)
