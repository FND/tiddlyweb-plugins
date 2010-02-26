"""
test module for listing RecipeS
"""

import os

from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, REPO_DIR, _cleanup


def test_list_recipes():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Storage(config["server_store"][1], env)

	for name in ["alpha", "bravo", "charlie"]:
		filepath = "%s.recipe" % os.path.join(STORE_DIR, name)
		open(filepath, "w").close()

	actual = [recipe.name for recipe in store.list_recipes()]
	expected = ["bravo", "alpha", "charlie"]
	assert set(actual) == set(expected)


def test_list_recipes_in_store():
	_cleanup()

	config = {
		"server_store": ["tiddlywebplugins.devstore", { "store_root": STORE_DIR }],
		"instance_tiddlers": {},
		"root_dir": ""
	}
	env = { "tiddlyweb.config": config }
	store = Store(config["server_store"][0], config["server_store"][1], env)

	for name in ["alpha", "bravo", "charlie"]:
		filepath = "%s.recipe" % os.path.join(STORE_DIR, name)
		open(filepath, "w").close()

	actual = [recipe.name for recipe in store.list_recipes()]
	expected = ["bravo", "alpha", "charlie"]
	assert set(actual) == set(expected)
