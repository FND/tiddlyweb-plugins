"""
Hybrid TiddlyWiki
serializer generating a TiddlyWiki document with baked-in static content

Renders the tiddlers listed in an index tiddler into the document's
NOSCRIPT section.

Static tiddlers are listed one per line in the tiddler specified via
config["static_index"] (default value is "StaticContentIndex").

TODO:
* support filter expressions (e.g. [tag[static]]) in _read_bracketed_list
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb import control
from tiddlyweb.wikitext import render_wikitext

from tiddlywebwiki.serialization import Serialization as WikiSerializer

from tiddlywebplugins import get_store


__version__ = "0.1.0"


def init(config):
	# register serializer
	content_type = "text/x-tiddlywiki"
	config["extension_types"]["wiki"] = content_type
	config["serializers"][content_type] = [__name__, "text/html; charset=UTF-8"]


class Serialization(WikiSerializer):

	def _no_script(self, url):
		try:
			static_index = self.environ["tiddlyweb.config"]["static_index"]
		except KeyError: # default
			static_index = "StaticContentIndex"

		store = self.environ["tiddlyweb.store"]
		routing_args = self.environ["wsgiorg.routing_args"][1]

		try: # recipe
			recipe = routing_args["recipe_name"]
			recipe = Recipe(recipe)
			recipe = store.get(recipe)
			tiddlers = control.get_tiddlers_from_recipe(recipe, self.environ)
		except KeyError: # bag
			bag = routing_args["bag_name"]
			bag = Bag(bag)
			bag = store.get(bag)
			tiddlers = control.get_tiddlers_from_bag(bag)
		tiddlers = _create_tiddler_dict(tiddlers)

		static_tiddlers = []
		try:
			index_tiddler = tiddlers[static_index]
			for title in _read_bracketed_list(index_tiddler.text):
				tiddler = tiddlers.get(title)
				try:
					text = render_wikitext(tiddler, self.environ)
					static_tiddlers.append('<div class="tiddler">%s</div>' % text)
				except AttributeError: # tiddler does not exist
					pass
		except KeyError: # static_index tiddler does not exist
			pass

		intro = super(self.__class__, self)._no_script(url)
		return "%s\n%s" % (intro, "\n".join(static_tiddlers))


def _read_bracketed_list(items):
	return items.split("\n") # TODO: proper implementation


def _create_tiddler_dict(tiddlers): # TODO: rename
	hashmap = {}
	for tiddler in tiddlers:
		hashmap[tiddler.title] = tiddler
	return hashmap
