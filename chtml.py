"""
Concise HTML
serializer providing a concise overview of bags, recipes or tiddlers

TODO:
* use HTMLPresenter
* links for browsing
* templating (jinja2)
"""

from tiddlyweb.serializations.html import Serialization as HTML_Serializer


__version__ = "0.1.1"


def init(config):
	# add serializer to config
	content_type = "text/x-chtml" # XXX: x-chtml is not suitable
	config["extension_types"]["chtml"] = content_type
	config["serializers"][content_type] = [__name__, "text/html; charset=UTF-8"]


class Serialization(HTML_Serializer):

	def list_tiddlers(self, bag):
		template = "<html><body><table>%s</table></body></html>" # TODO: column headings
		tiddlers = [_render_tiddler(t, bag.revbag) for t in bag.list_tiddlers()] # XXX: revbag handling incorrect?
		return template % "\n".join(tiddlers)

	def tiddler_as(self, tiddler):
		template = "<html><body><table>%s</table>%s</body></html>" # TODO: column headings
		full_text = HTML_Serializer.tiddler_as(self, tiddler)
		return template % (_render_tiddler(tiddler), full_text) # XXX: leads to odd composition of content


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
