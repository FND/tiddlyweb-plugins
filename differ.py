"""
TiddlyWeb plugin to compare tiddler revisions

Usage:
  GET /diff?rev1=<tiddler>&rev2=<tiddler>
  POST /diff?rev1=<tiddler>

tiddler references are of the form bags/<title>[/<revision>]
(recipes are currently not supported in this context)

POST data (JSON representation of a tiddler) can be used instead of a tiddler
reference (rev1 or rev2 URL parameter)

To Do:
* tests
"""

import difflib

from tiddlyweb import control
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.web import util as web
from tiddlyweb.web.http import HTTP400


__version__ = "0.2.0"


def init(config):
	# extend urls.map
	config["selector"].add("/diff", GET=get_request, POST=post_request)


def get_request(environ, start_response):
	rev1, rev2 = _get_revision_params(environ)
	store = environ["tiddlyweb.store"]
	try:
		rev1 = _get_tiddler(rev1, store)
		rev2 = _get_tiddler(rev2, store)
	except AttributeError:
		raise HTTP400("missing revision parameter")
	content = compare(rev1, rev2)
	return _generate_response(content, environ, start_response)


def post_request(environ, start_response):
	length = int(environ["CONTENT_LENGTH"])
	post_content = environ["wsgi.input"].read(length)
	serializer = Serializer("json") # TODO: use content-type to determine serialization
	rev = Tiddler("untitled") # N.B.: Serializations need not contain title.
	serializer.object = rev
	serializer.from_string(post_content.decode("utf-8"))

	rev1_id, rev2_id = _get_revision_params(environ)
	store = environ["tiddlyweb.store"]
	try:
		if not rev1_id:
			rev1 = rev
			rev2 = _get_tiddler(rev2_id, store)
		elif not rev2_id:
			rev1 = _get_tiddler(rev1_id, store)
			rev2 = rev
		else:
			raise HTTP400("ambiguous request")
	except AttributeError:
		raise HTTP400("missing revision parameter")

	content = compare(rev1, rev2)
	return _generate_response(content, environ, start_response)


def compare(rev1, rev2):
	"""
	compare two tiddlers
	"""
	serializer = Serializer("text")
	serializer.object = rev1
	rev1 = serializer.to_string()
	serializer.object = rev2
	rev2 = serializer.to_string()
	return "<pre>\n%s\n</pre>" % diff(rev1, rev2)


def diff(a, b):
	d = difflib.Differ()
	result = list(d.compare(a.splitlines(), b.splitlines()))
	return "\n".join(result)


def generate_inline_diff(a, b): # XXX: currently unused -- TODO: special handling for line-break changes
	"""
	compare two single-line strings

	returns an "inline" diff using minimal HTML markup (INS and DEL elements)
	"""
	seq = difflib.SequenceMatcher(None, a, b)
	output = []
	for opcode, a0, a1, b0, b1 in seq.get_opcodes():
		if opcode == "equal":
			output.append(seq.a[a0:a1])
		elif opcode == "insert":
			output.append("<ins>%s</ins>" % seq.b[b0:b1])
		elif opcode == "delete":
			output.append("<del>%s</del>" % seq.a[a0:a1])
		elif opcode == "replace":
			output.append("<del>%s</del><ins>%s</ins>" % (seq.a[a0:a1], seq.b[b0:b1]))
		else:
			raise RuntimeError("unexpected opcode") # XXX: RuntimeError inappropriate?
	return "".join(output)


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
	return store.get(tiddler)


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

	rev1_id = get_param("rev1")
	rev2_id = get_param("rev2")
	return rev1_id, rev2_id


def _generate_response(content, environ, start_response):
	serialize_type, mime_type = web.get_serialize_type(environ)
	cache_header = ("Cache-Control", "no-cache") # ensure accesing latest HEAD revision
	content_header = ("Content-Type", mime_type)
	response = [cache_header, content_header]
	start_response("200 OK", response)
	return [content]
