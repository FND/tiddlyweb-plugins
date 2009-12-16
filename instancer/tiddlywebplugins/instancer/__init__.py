"""
utility package for TiddlyWeb instances
"""

import os

import tiddlywebplugins.instancer.sourcer

from time import time
from random import random

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb.model.user import User
from tiddlyweb.util import sha

from tiddlywebplugins.utils import get_store


__version__ = "0.5.1"

CONFIG_NAME = "tiddlywebconfig.py"


class Instance(object):
	"""
	prefconfigured TiddlyWeb instance
	"""

	def __init__(self, directory, init_config, instance_config=None): # TODO: "create" argument to spawn and update?
		"""
		creates instance in given directory

		init_config is a TiddlyWeb configuration dictionary used when creating
		the instance
		instance_config is an optional dictionary with configuration values for
		the default tiddlywebconfig.py (usually referencing init_config in
		system_plugins and twanager_plugins)

		Note that init_config may contain an entry "instance_config_head" whose
		value is prepended to the generated tiddlywebconfig.py.
		"""
		self.root = os.path.abspath(directory)
		self.init_config = init_config
		self.instance_config = instance_config

	def spawn(self, store_structure=None):
		"""
		creates the instance, optionally pre-configuring the store structure
		"""
		os.mkdir(self.root)
		os.chdir(self.root) # XXX: side-effects

		self._write_config()

		if store_structure: # XXX: also prevents instance_tiddlers bag creation
			self._init_store(store_structure)

	def update_store(self):
		"""
		prepopulates/updates store contents by (re)importing instance_tiddlers
		"""
		os.chdir(self.root) # XXX: side-effects

		store = get_store(self.init_config)
		for bag, uris in self.init_config["instance_tiddlers"].items():
			for tiddler in sourcer.from_list(uris):
				tiddler.bag = bag
				store.put(tiddler)

	def _init_store(self, struct):
		"""
		creates basic store structure with bags, recipes and users

		(no support for user passwords for security reasons)
		"""
		store = get_store(self.init_config)

		for bag_name in self.init_config["instance_tiddlers"]: # XXX: obsolete?
			bag = Bag(bag_name)
			store.put(bag)

		bags = struct.get("bags", {})
		for name, data in bags.items():
			desc = data.get("desc")
			bag = Bag(name, desc=desc)
			constraints = data.get("policy", {})
			_set_policy(bag, constraints)
			store.put(bag)

		recipes = struct.get("recipes", {})
		for name, data in recipes.items(): # TODO: DRY
			desc = data.get("desc")
			recipe = Recipe(name, desc=desc)
			recipe.set_recipe(data["recipe"])
			constraints = data.get("policy", {})
			_set_policy(recipe, constraints)
			store.put(recipe)

		users = struct.get("users", {})
		for name, data in users.items():
			note = data.get("note")
			user = User(name, note=note)
			for role in data.get("roles"):
				user.add_role(role)
			store.put(user)

	def _write_config(self, defaults=None):
		"""
		creates a default tiddlywebconfig.py in the working directory

		uses values from instance_config plus optional instance_config_head
		from init_config
		"""
		intro = "%s\n%s\n%s" % ("# A basic configuration.",
			'# Run "pydoc tiddlyweb.config" for details on configuration items.',
			self.init_config.get("instance_config_head", ""))

		config = {
			"secret": _generate_secret()
		}
		config.update(self.instance_config or {})

		config_string = "config = %s\n" % _pretty_print(config)
		f = open(CONFIG_NAME, "w")
		f.write("%s\n%s" % (intro, config_string))
		f.close()


def _set_policy(entity, constraints):
	"""
	applies contstraints to entity

	entity is a Bag or a Recipe, constraints a dictionary
	"""
	for constraint, value in constraints.items():
		setattr(entity.policy, constraint, value)


def _generate_secret():
	"""
	create a pseudo-random secret

	This is used for message authentication.
	"""
	digest = sha(str(time()))
	digest.update(str(random()))
	digest.update("lorem foo ipsum")
	return digest.hexdigest()


def _pretty_print(dic): # TODO: use pprint?
	"""
	generate an indented string representation of a dictionary
	"""
	def escape_strings(value):
		if hasattr(value, "join"): # XXX: checking for join method hacky!?
			return '"%s"' % value
		else:
			return value
	lines = ('\t"%s": %s' % (k, escape_strings(v)) for k, v in dic.items())
	return "{\n%s\n}" % ",\n".join(lines)
