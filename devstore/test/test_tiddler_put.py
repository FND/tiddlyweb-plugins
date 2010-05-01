"""
test module for retrieving TiddlerS
"""

import os

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, REPO_DIR, _cleanup


def test_tiddler_put():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"myBag": []
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	tiddler = Tiddler("lorem")
	tiddler.bag = "myBag"
	store.tiddler_put(tiddler)

	tiddler_path = os.path.join(STORE_DIR, tiddler.bag, "%s.tid" % tiddler.title)
	assert os.path.exists(tiddler_path)


def test_put_tiddler_to_store():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"myBag": ["%s/alpha/index.recipe" % REPO_DIR]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	tiddler = Tiddler("lorem")
	tiddler.bag = "myBag"
	store.put(tiddler)

	tiddler_path = os.path.join(STORE_DIR, tiddler.bag, "%s.tid" % tiddler.title)
	assert os.path.exists(tiddler_path)

	tiddler = Tiddler("foo bar")
	tiddler.bag = "myBag"
	store.put(tiddler)

	tiddler_path = os.path.join(STORE_DIR, "myBag", "foo%20bar.tid")
	assert os.path.exists(tiddler_path)
	assert store.get(tiddler).title == "foo bar"

	# XXX: testing get operation here for convenience
	bag = Bag("myBag")
	try:
		assert "foo bar" in [t.title for t in store.list_bag_tiddlers(bag)]
	except AttributeError: # TiddlyWeb 1.0 has no list_bag_tiddlers method
		pass

	tiddler = Tiddler("foo/bar")
	tiddler.bag = "myBag"
	store.put(tiddler)

	tiddler_path = os.path.join(STORE_DIR, "myBag", "foo%2Fbar.tid")
	assert os.path.exists(tiddler_path)
	assert store.get(tiddler).title == "foo/bar"
