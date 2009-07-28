"""
Concise HTML
serializer providing a concise overview of bags, recipes or tiddlers

TODO:
* use HTMLPresenter
* replace HTML serializer
* provide full-tiddler representation for collections
* links for browsing
* templating (jinja2)
"""

from tiddlyweb.serializations.html import Serialization as HTML_Serializer


__version__ = "0.1.2"


def init(config):
	# add serializer to config
	content_type = "text/x-chtml" # XXX: x-chtml is not suitable
	config["extension_types"]["chtml"] = content_type
	config["serializers"][content_type] = [__name__, "text/html; charset=UTF-8"]


class Serialization(HTML_Serializer):

	def list_tiddlers(self, bag):
		template = "<html><body><table>%s</table></body></html>" # TODO: column headings
		tiddlers = [_render_tiddler(t) for t in bag.list_tiddlers()]
		return template % "\n".join(tiddlers)

	def tiddler_as(self, tiddler):
		template = "<html><body><table>%s</table>%s</body></html>" # TODO: column headings
		full_text = HTML_Serializer.tiddler_as(self, tiddler)
		return template % (_render_tiddler(tiddler), full_text) # XXX: leads to odd composition of content


def _render_tiddler(tiddler):
	"""
	represent Tiddler instance as HTML table row
	"""
	template = "<tr><td>%s</td><td>%s</td><td>#%s</td><td>%s</td>"
	return template % (tiddler.modified, tiddler.title, tiddler.revision,
		tiddler.modifier)
