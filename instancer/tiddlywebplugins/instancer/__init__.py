"""
utility package for TiddlyWeb instances
"""

import os

import sourcer # XXX: use explicit tiddlywebplugins.instancer.sourcer (breaks tests due to "twp" namespace issue)

from time import time
from random import random

from tiddlyweb.model.bag import Bag
from tiddlyweb.util import sha
from tiddlywebplugins.utils import get_store


__version__ = "0.1.1"

CONFIG_NAME = "tiddlywebconfig.py"


class Instance(object):
	"""
	a prefconfigured TiddlyWeb instance directory

	accepts an optional dictionary with configuration values for the instance's
	default tiddlywebconfig.py
	"""

	def __init__(self, directory, init_config, instance_config=None):
		"""
		creates instance in given directory

		accepts an optional dictionary with configuration values for the instance's
		default tiddlywebconfig.py
		"""
		# TODO: rename config arguments/variables
		self.root = os.path.abspath(directory)
		self.init_config = init_config
		self.instance_config = instance_config
		self.store = get_store(self.init_config)

	def spawn(self):
		os.mkdir(self.root)

		os.chdir(self.root) # XXX: side-effects
		_write_config(self.instance_config)

		for bag_name in dict(self.init_config["instance_tiddlers"]):
			bag = Bag(bag_name)
			self.store.put(bag)

	def update_store(self):
		"""
		prepopulates/updates store contents by (re)importing instance_tiddlers
		"""
		os.chdir(self.root) # XXX: side-effects

		for bag, uris in self.init_config["instance_tiddlers"]:
			for tiddler in sourcer.from_list(uris):
				tiddler.bag = bag
				self.store.put(tiddler)


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
