"""
Hybrid TiddlyWiki
serializer generating accessible TiddlyWiki documents

Renders a static representation of tiddlers into the document's
NOSCRIPT section.

Static tiddlers are listed one per line in the tiddler specified via
config["static_index"] (defaults to "DefaultTiddlers").

TODO:
* unit tests
* efficiency enhancements when retrieving tiddlers
* support filter expressions (e.g. [tag[static]]) in _read_bracketed_list
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.recipe import Recipe
from tiddlyweb import control
from tiddlyweb.wikitext import render_wikitext

from tiddlywebwiki.serialization import Serialization as WikiSerializer


__version__ = "0.1.1"

default_static_index = "DefaultTiddlers"
tiddler_template = """
<h3>%s</h3>
<div class="tiddler">
%s
</div>
"""


def init(config):
	# register serializer
	content_type = "text/x-tiddlywiki"
	config["extension_types"]["wiki"] = content_type
	config["serializers"][content_type] = [__name__, "text/html; charset=UTF-8"]


class Serialization(WikiSerializer):

	def _no_script(self, url):
		"""
		returns static HTML representation of a list of tiddlers
		"""
		try:
			static_index = self.environ["tiddlyweb.config"]["static_index"]
		except KeyError: # default
			static_index = default_static_index

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
		tiddlers = dict([(tiddler.title, tiddler) for tiddler in tiddlers])

		static_tiddlers = []
		try:
			index_tiddler = tiddlers[static_index]
			for title in _read_bracketed_list(index_tiddler.text):
				tiddler = tiddlers.get(title)
				try:
					text = render_wikitext(tiddler, self.environ)
					static_tiddlers.append(tiddler_template %
						(tiddler.title, text))
				except AttributeError: # tiddler does not exist
					pass
		except KeyError: # static_index tiddler does not exist
			pass

		intro = super(self.__class__, self)._no_script(url)
		return "%s\n%s" % (intro, "\n".join(static_tiddlers))


def _read_bracketed_list(items):
	"""
	retrieve items from bracketed list

	items argument is a space-separated list with individual items optionally
	enclosed in double brackets
	"""
	return [item.strip("[").strip("]") for item in items.split("\n")] # TODO: proper implementation
