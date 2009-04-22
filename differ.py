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
* use /diff
* diff implementation (various formats?)
"""

from tiddlyweb import control
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.web import util as web
from tiddlyweb.web.http import HTTP400


def init(config):
	print "initializing differ" # XXX: bad form?
	# extend urls.map
	config["selector"].add("/differ", GET=get_request, POST=post_request)


def get_request(environ, start_response):
	rev1, rev2 = _get_revision_params(environ)
	store = environ["tiddlyweb.store"]
	rev1 = _get_tiddler(rev1, store)
	rev2 = _get_tiddler(rev2, store)
	content = compare(rev1, rev2)
	return _generate_response(content, environ, start_response)


def post_request(environ, start_response):
	length = int(environ["CONTENT_LENGTH"])
	rev = environ["wsgi.input"].read(length) # TODO: convert JSON to text serialization
	rev1, rev2 = _get_revision_params(environ)
	store = environ["tiddlyweb.store"]
	if rev1:
		rev1 = _get_tiddler(rev1, store)
	else:
		rev1 = rev
	if rev2: # XXX: duplication; might result in POST data being used for both revisions
		rev2 = _get_tiddler(rev2, store)
	else:
		rev2 = rev
	content = compare(rev1, rev2)
	return _generate_response(content, environ, start_response)


def compare(rev1, rev2):
	return "<pre>%s</pre>" % (rev1, rev2)


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


def _get_revision_params(environ):
	"""
	retrieve tiddler identifiers from query string
	"""
	store = environ["tiddlyweb.store"]

	def get_param(name):
		rev = environ["tiddlyweb.query"].get(name)
		if rev:
			rev = rev[0]
		return rev

	rev1 = get_param("rev1")
	rev2 = get_param("rev2")
	return rev1, rev2


def _generate_response(content, environ, start_response):
	serialize_type, mime_type = web.get_serialize_type(environ)
	cache_header = ("Cache-Control", "no-cache") # ensure accesing latest HEAD revision
	content_header = ("Content-Type", mime_type)
	response = [cache_header, content_header]
	start_response("200 OK", response)
	return [content]
