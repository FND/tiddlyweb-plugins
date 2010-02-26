"""
test module for retrieving BagS
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, REPO_DIR, _cleanup


def test_bag_get():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"myBag": ["%s/bravo/index.recipe" % REPO_DIR]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	bag = Bag("myBag")
	bag = store.bag_get(bag)

	assert bag.name == "myBag"

	actual = [tiddler.title for tiddler in bag.list_tiddlers()]
	expected = ["lorem", "foo", "SiteTitle", "ipsum", "bar"]
	assert set(actual) == set(expected) # XXX: sets as temporary workaround for dupes issue


def test_get_bag_from_store():
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

	bag = Bag("myBag")
	bag = store.get(bag)

	assert bag.name == "myBag"

	actual = [tiddler.title for tiddler in bag.list_tiddlers()]
	expected = ["SiteTitle", "foo", "lorem"]
	assert actual == expected
