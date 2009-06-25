"""
Concise HTML
serializer providing a concise overview of bags, recipes or tiddlers

TODO:
* rename?
* implement *_as, list_* (cf. tiddlyweb.serializations.__init__)
* refactor for DRY (esp. templates)
* links for browsing
* valid HTML
* templating
"""

from tiddlyweb.serializations import SerializationInterface


__version__ = "0.1.0"


def init(config):
	# add serializer to config
	content_type = "text/x-chtml" # XXX: x-chtml is not suitable
	config["extension_types"]["chtml"] = content_type
	config["serializers"][content_type] = ["chtml", "text/html; charset=UTF-8"]


class Serialization(SerializationInterface):

	def list_bags(self, bags):
		template = "<html><body><table>%s</table></body></html>" # TODO: column headings
		bags = ["<tr><td>%s</td><td>%s</td>" % (bag.name, bag.desc)
			for bag in bags]
		return template % "\n".join(bags)

	def list_recipes(self, recipes):
		template = "<html><body><table>%s</table></body></html>" # TODO: column headings
		recipes = ["<tr><td>%s</td><td>%s</td>" % (recipe.name, recipe.desc)
			for recipe in recipes]
		return template % "\n".join(recipes)

	def list_tiddlers(self, bag):
		template = "<html><body><table>%s</table></body></html>" # TODO: column headings
		tiddlers = [_render_tiddler(t, bag.revbag) for t in bag.list_tiddlers()] # XXX: revbag handling incorrect?
		return template % "\n".join(tiddlers)

	def tiddler_as(self, tiddler):
		template = "<html><body><table>%s</table></body></html>" # TODO: column headings
		return template % _render_tiddler(tiddler)


def _render_tiddler(tiddler, hide_rev=False):
	"""
	represent Tiddler instance as HTML table row

	If hide_rev is True, revision numbers are omitted.
	"""
	if hide_rev:
		template = "<tr><td>%s</td><td>%s</td><td>%s</td>"
		output = template % (tiddler.modified, tiddler.title, tiddler.modifier)
	else:
		template = "<tr><td>%s</td><td>%s</td><td>#%s</td><td>%s</td>"
		output = template % (tiddler.modified, tiddler.title, tiddler.revision,
			tiddler.modifier)
	return output
