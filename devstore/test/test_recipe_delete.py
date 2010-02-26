"""
test module for retrieving RecipeS
"""

import os

from py.test import raises

from tiddlyweb.model.recipe import Recipe
from tiddlyweb.store import Store, NoRecipeError

from tiddlywebplugins.devstore import Store as Storage

from test.test_devstore import STORE_DIR, _cleanup



def test_recipe_delete_from_store():
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
	store.delete(recipe)

	recipe = Recipe(name)
	raises(NoRecipeError, "store.get(recipe)")
