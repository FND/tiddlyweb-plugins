"""
random data generator

uses a virtual store implementation

TODO:
* documentation
* rename?
"""

from random import random

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.bag import Bag
from tiddlyweb.stores import StorageInterface
from tiddlyweb.serializer import Serializer
from tiddlyweb.web.sendtiddlers import send_tiddlers

from tiddlywebplugins import get_store


default_tiddler_count = 10


def init(config):
	# extend urls.map
	config["selector"].add("/generator[.{format}]", GET=get_request) # XXX: rename?


def get_request(environ, start_response):
	# register store
	environ["tiddlyweb.config"]["server_store"] = [__name__, None]

	query = environ["tiddlyweb.query"]
	tiddler_count = query.get("tiddlers", [None])[0] or default_tiddler_count

	store = get_store(environ["tiddlyweb.config"])
	bag = Bag(str(tiddler_count))
	bag = store.get(bag)
	# populate tiddlers in bag
	for tiddler in bag.list_tiddlers():
		store.get(tiddler)

	return send_tiddlers(environ, start_response, bag)


class Store(StorageInterface):

	def __init__(self, environ=None):
		super(Store, self).__init__(environ) # XXX: obsolete?

	#def list_recipes(self): # TODO

	#def list_bags(self): # TODO

	#def list_tiddler_revisions(self, tiddler): # TODO

	#def recipe_get(self, bag): # TODO

	def bag_get(self, bag):
		tiddlers = []
		tiddler_count = int(bag.name)
		for i in xrange(tiddler_count):
			tiddler = Tiddler(_generate_title())
			tiddler.bag = bag.name
			bag.add_tiddler(tiddler)
		return bag

	def tiddler_get(self, tiddler):
		tiddler = _populate_tiddler(tiddler)
		return tiddler


def _generate_title():
	return str(int(random() * 1000000)) # TODO: make pattern customizable


def _populate_tiddler(tiddler):
	tiddler.text = "lorem ipsum" # TODO: random words from /usr/share/dict/words
	tiddler.tags = [] # TODO
	#tiddler.fields = {} # TODO
	return tiddler
