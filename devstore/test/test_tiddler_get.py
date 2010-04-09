"""
test module for retrieving TiddlerS
"""

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, REPO_DIR, _cleanup


def test_tiddler_get():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"myBag": ["%s/alpha/index.recipe" % REPO_DIR]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	tiddler = Tiddler("lorem")
	tiddler.bag = "myBag"
	t = store.tiddler_get(tiddler)

	assert t.title == "lorem"
	assert t.bag == "myBag"
	assert t.tags == []
	assert t.modifier == "FND"
	assert t.text == "lorem ipsum"

	tiddler = Tiddler("foo")
	tiddler.bag = "myBag"
	t = store.tiddler_get(tiddler)

	assert t.title == "foo"
	assert t.bag == "myBag"
	assert t.type == "text/javascript"
	assert t.revision == 1
	assert t.tags == ["systemConfig"]
	assert t.modifier == None
	assert t.text == 'console.log("foo");\n'


def test_get_tiddler_from_store():
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
	t = store.get(tiddler)

	assert t.title == "lorem"
	assert t.bag == "myBag"
	assert t.revision == 1
	assert t.tags == []
	assert t.modifier == "FND"
	assert t.text == "lorem ipsum"

	tiddler = Tiddler("foo")
	tiddler.bag = "myBag"
	t = store.get(tiddler)

	assert t.title == "foo"
	assert t.bag == "myBag"
	assert t.revision == 1
	assert t.tags == ["systemConfig"]
	assert t.modifier == None
	assert t.text == 'console.log("foo");\n'


def test_get_tiddler_revision():
	_cleanup()

	config = { "server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {
			"myBag": ["%s/alpha/index.recipe" % REPO_DIR]
		},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	tiddler = Tiddler("lorem")
	tiddler.bag = "myBag"
	t = store.get(tiddler)

	assert t.title == "lorem"
	assert t.bag == "myBag"
	assert t.revision == 1
	assert t.tags == []
	assert t.modifier == "FND"
	assert t.text == "lorem ipsum"

	tiddler = Tiddler("hello world")
	tiddler.bag = "myBag"
	tiddler.tags = ["foo", "bar"]
	tiddler.modifier = "FND"
	tiddler.text = "lorem ipsum"
	store.put(tiddler)
	tiddler = Tiddler("hello world")
	tiddler.bag = "myBag"
	t = store.get(tiddler)

	assert t.title == "hello world"
	assert t.bag == "myBag"
	assert t.revision == 1
	assert t.tags == ["foo", "bar"]
	assert t.modifier == "FND"
	assert t.text == "lorem ipsum"
