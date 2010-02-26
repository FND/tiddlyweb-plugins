"""
test module for retrieving RecipeS
"""

import os

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.store import Store

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, _cleanup



def test_recipe_get_from_store():
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

	recipe = Recipe(name)
	recipe = store.get(recipe)

	assert recipe.name == "foo"
	assert recipe.desc == "lorem ipsum"
