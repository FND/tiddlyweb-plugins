"""
TiddlyWeb plugin to compare tiddler revisions

Usage:
  GET /differ?rev1=<tiddler>&rev2=<tiddler>
  POST /differ?rev1=<tiddler>

tiddler references are of the form bags/<title>[/<revision>]
(recipes are currently not supported in this context)

POST data (JSON representation of a tiddler) can be used instead of a tiddler
reference (rev1 or rev2 URL parameter)

To Do:
* rename to diff
* POST implementation
* diff implementation (various formats?)
"""

from difflib import Differ, HtmlDiff

from tiddlyweb import control
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web import util as web
from tiddlyweb.web.http import HTTP400
from tiddlyweb.serializer import Serializer

def init(config):
	print "initializing differ" # XXX: bad form?
	# extend urls.map
	config["selector"].add("/differ", GET=compare, POST=compare)


def compare(environ, start_response):
	store = environ["tiddlyweb.store"]
	# resolve URL parameters
	def get_param(name):
		rev = environ["tiddlyweb.query"].get(name)
		if rev:
			rev = _get_tiddler(rev[0], store)
		return rev
	rev1 = get_param("rev1")
	rev2 = get_param("rev2")
	# resolve POST data
	# TODO
	# generate diff
	content = "<pre>%s</pre>" % diff(rev1, rev2)
	return _generate_response(content, environ, start_response)


def diff(a, b): # TODO
	return "%s\n\n%s" % (a, b) # DEBUG


def _get_tiddler(id, store): # XXX: rename
	"""
	retrieve a tiddler revision based on an identifier

	returns the text serialization of the respective revision
	"""
	# retrieve tiddler revision from store
	type, name, title, rev = _resolve_identifier(id)
	if type == "bag":
		tiddler = Tiddler(title, name)
	else:
		raise HTTP400("recipes not supported") # TODO?
	tiddler.revision = rev
	tiddler = store.get(tiddler)
	# serialize tiddler
	serializer = Serializer("text")
	serializer.object = tiddler
	return serializer.to_string()


def _resolve_identifier(id):
	"""
	resolve tiddler identifier string

	the identifier is a string of the form
	<bags|recipes>/<name>/<title>[/<revision>]

	returns type (bag or recipe), name, tiddler title and revision number
	"""
	try:
		type, name, title, rev = id.split("/")
		rev = int(rev)
	except ValueError: # revision implicit
		type, name, title = id.split("/")
		rev = 0 # HEAD
	type = type[:-1] # strip plural
	return type, name, title, rev


def _generate_response(content, environ, start_response):
	serialize_type, mime_type = web.get_serialize_type(environ)
	cache_header = ("Cache-Control", "no-cache") # ensure accesing latest HEAD revision
	content_header = ("Content-Type", mime_type)
	response = [cache_header, content_header]
	start_response("200 OK", response)
	return content # XXX: should be list!?
