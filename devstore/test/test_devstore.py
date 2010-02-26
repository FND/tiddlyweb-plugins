"""
test module for Dev Store
"""

import os

from shutil import rmtree

from py.test import raises

from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage
from tiddlywebplugins.devstore import ConfigurationError


STORE_DIR = "store"
REPO_DIR = "test/fixtures/repo"


def test_root_config():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", {}],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	raises(KeyError, 'Store(config["server_store"][0], config["server_store"][1], environ=env)')
	raises(OSError, "os.rmdir(STORE_DIR)") # errors out before creating directory


def test_instance_tiddlers_config():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	raises(ConfigurationError, 'Storage(config["server_store"][1], environ=env)')
	raises(OSError, "os.rmdir(STORE_DIR)") # errors out before creating directory


def test_instance_tiddlers_index():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"alpha": [
				"%s/alpha/index.recipe" % REPO_DIR,
				"%s/alpha/title.tid" % REPO_DIR
			],
			"bravo": [
				"%s/bravo/index.recipe" % REPO_DIR,
				"%s/bravo/title.tid" % REPO_DIR
			]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	expected = {
		"alpha": [
			"%s/alpha/index.recipe" % REPO_DIR,
			"%s/alpha/title.tid" % REPO_DIR
		],
		"bravo": [
			"%s/bravo/index.recipe" % REPO_DIR,
			"%s/bravo/title.tid" % REPO_DIR
		]
	}
	assert store._index == expected


def test_root_dir():
	_cleanup()

	try:
		rmtree(STORE_DIR)
	except OSError:
		pass
	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], environ=env)

	assert os.path.exists(STORE_DIR)


def test_bag_dirs():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"foo": [],
			"bar": []
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], environ=env)

	bag_path = os.path.join(STORE_DIR, "foo")
	assert os.path.exists(bag_path)

	bag_path = os.path.join(STORE_DIR, "bar")
	assert os.path.exists(bag_path)


def _cleanup():
	try:
		rmtree(STORE_DIR)
	except OSError:
		pass
