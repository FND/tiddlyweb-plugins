"""
test module for listing BagS
"""

from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, REPO_DIR, _cleanup


def test_list_bags():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"alpha": ["%s/alpha/index.recipe" % REPO_DIR],
			"bravo": ["%s/bravo/index.recipe" % REPO_DIR]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	actual = [bag.name for bag in store.list_bags()]
	expected = ["bravo", "alpha"]
	assert sorted(actual) == sorted(expected)


def test_list_bags_in_store():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"alpha": ["%s/alpha/index.recipe" % REPO_DIR],
			"bravo": ["%s/bravo/index.recipe" % REPO_DIR]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	actual = [bag.name for bag in store.list_bags()]
	expected = ["bravo", "alpha"]
	assert sorted(actual) == sorted(expected)
