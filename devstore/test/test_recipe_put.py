"""
test module for creating RecipeS
"""

import os

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, _cleanup


def test_recipe_put():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	name = "foo"
	recipe = Recipe(name)
	store.recipe_put(recipe)

	assert os.path.exists("%s/%s.recipe" % (STORE_DIR, name))


def test_recipe_put_to_store():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	name = "foo"
	recipe = Recipe(name)
	store.put(recipe)

	assert os.path.exists("%s.recipe" % os.path.join(STORE_DIR, name))


def test_serialization():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	name = "foo"
	recipe = Recipe(name)
	recipe.desc = "lorem ipsum"
	store.put(recipe)

	f = open("%s.recipe" % os.path.join(STORE_DIR, name))
	actual = f.read()
	f.close()
	expected = """desc: lorem ipsum
policy: {"read": [], "create": [], "manage": [], "accept": [], "write": [], "owner": null, "delete": []}
"""
	assert actual == expected
