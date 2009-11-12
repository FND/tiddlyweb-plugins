"""
utility package for TiddlyWeb instances
"""

import os

import tiddlywebplugins.instancer.sourcer

from time import time
from random import random

from tiddlyweb.model.bag import Bag
from tiddlyweb.util import sha
from tiddlywebplugins.utils import get_store


__version__ = "0.1.3"

CONFIG_NAME = "tiddlywebconfig.py"


class Instance(object):
	"""
	prefconfigured TiddlyWeb instance
	"""

	def __init__(self, directory, init_config, instance_config=None):
		"""
		creates instance in given directory

		init_config is a TiddlyWeb configuration dictionary used when creating
		the instance
		instance_config is an optional dictionary with configuration values for
		the default tiddlywebconfig.py (usually referencing init_config in
		system_plugins and twanager_plugins)
		"""
		self.root = os.path.abspath(directory)
		self.init_config = init_config
		self.instance_config = instance_config

	def spawn(self):
		os.mkdir(self.root)
		os.chdir(self.root) # XXX: side-effects

		_write_config(self.instance_config)

		store = get_store(self.init_config)
		for bag_name in dict(self.init_config["instance_tiddlers"]):
			bag = Bag(bag_name)
			store.put(bag)

	def update_store(self):
		"""
		prepopulates/updates store contents by (re)importing instance_tiddlers
		"""
		os.chdir(self.root) # XXX: side-effects

		store = get_store(self.init_config)
		for bag, uris in self.init_config["instance_tiddlers"]:
			for tiddler in sourcer.from_list(uris):
				tiddler.bag = bag
				store.put(tiddler)


def _generate_secret():
	"""
	create a pseudo-random secret

	This is used for message authentication.
	"""
	digest = sha(str(time()))
	digest.update(str(random()))
	digest.update("lorem foo ipsum")
	return digest.hexdigest()


def _write_config(defaults=None):
	"""
	create a default tiddlywebconfig.py in the working directory

	accepts an optional dictionary with configuration values
	"""
	intro = "%s\n%s" % ("# A basic configuration.",
		'# Run "pydoc tiddlyweb.config" for details on configuration items.')

	config = {
		"secret": _generate_secret()
	}
	config.update(defaults or {})

	config_string = "config = %s\n" % _pretty_print(config)
	f = open(CONFIG_NAME, "w")
	f.write("%s\n%s" % (intro, config_string))
	f.close()


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
