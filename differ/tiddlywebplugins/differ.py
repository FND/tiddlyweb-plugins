"""
Differ
TiddlyWeb plugin to compare tiddler revisions

Usage:
  GET /diff?rev1=<tiddler>&rev2=<tiddler>[&format=<format>]
  POST /diff?rev1=<tiddler>[&format=<format>]

tiddler references are of the form bags/<title>[/<revision>]
(recipes are currently not supported in this context)

supported formats:
* human-readable line-by-line comparison (default; plain text)
* "unified" (plain text)
* "inline" (HTML)
* "horizontal" (side-by-side; HTML)

POST data (JSON representation of a tiddler) can be used instead of a tiddler
reference (rev1 or rev2 URL parameter)

TODO:
* unicode handling
* tests
* avoid docstring duplication in README
"""

import cgi
import difflib

from tiddlyweb import control
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.web import util as web
from tiddlyweb.web.http import HTTP400


__version__ = "0.4.1"


def init(config):
	try: # system plugin
		config["selector"].add("/diff", GET=get_request, POST=post_request)
	except KeyError: # twanager plugin
		pass


def get_request(environ, start_response):
	query = environ["tiddlyweb.query"]
	store = environ["tiddlyweb.store"]

	rev1_id = query.get("rev1", [None])[0]
	rev2_id = query.get("rev2", [None])[0]
	try:
		rev1 = _get_tiddler(rev1_id, store)
		rev2 = _get_tiddler(rev2_id, store)
	except AttributeError:
		raise HTTP400("missing revision parameter")

	format = query.get("format", [None])[0]

	content = compare_tiddlers(rev1, rev2, format)
	return _generate_response(content, environ, start_response)


def post_request(environ, start_response):
	length = int(environ["CONTENT_LENGTH"])
	post_content = environ["wsgi.input"].read(length)
	serializer = Serializer("json") # TODO: use content-type to determine serialization
	rev = Tiddler("untitled") # N.B.: Serializations need not contain title.
	serializer.object = rev
	serializer.from_string(post_content.decode("utf-8"))

	query = environ["tiddlyweb.query"]
	store = environ["tiddlyweb.store"]

	rev1_id = query.get("rev1", [None])[0]
	rev2_id = query.get("rev2", [None])[0]
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

	format = query.get("format", [None])[0]

	content = compare_tiddlers(rev1, rev2, format)
	return _generate_response(content, environ, start_response)


def compare_tiddlers(rev1, rev2, format=None):
	"""
	compare two Tiddler instances
	"""
	serializer = Serializer("text")
	serializer.object = rev1
	rev1 = serializer.to_string()
	serializer.object = rev2
	rev2 = serializer.to_string()
	return diff(rev1, rev2, format)


def diff(a, b, format=None): # XXX: rename?
	"""
	create a diff representation of a string comparison

	defaults to human-readable line-by-line comparison
	alternative formats available are "unified", "horizontal" and "inline"
	"""
	if format == "unified":
		return "\n".join(difflib.unified_diff(a.splitlines(), b.splitlines()))
	elif format == "horizontal": # XXX: rename
		d = difflib.HtmlDiff()
		return d.make_file(a.splitlines(), b.splitlines()) # XXX: use make_table?!
	elif format == "inline":
		return generate_inline_diff(a, b)
	else:
		d = difflib.Differ() # XXX: use difflib.ndiff?
		result = list(d.compare(a.splitlines(), b.splitlines()))
		return "\n".join(result)


def generate_inline_diff(a, b): # TODO: optionally strip unchanged blocks
	"""
	compare two strings, highlighting differences inline

	returns a string using minimal HTML markup (INS and DEL elements)
	"""
	seq = difflib.SequenceMatcher(None, a, b)
	output = []
	for opcode, a0, a1, b0, b1 in seq.get_opcodes():
		if opcode == "equal":
			output.append(_html_transform(seq.a[a0:a1]))
		elif opcode == "insert":
			output.append("<ins>%s</ins>" % _html_transform(seq.b[b0:b1]))
		elif opcode == "delete":
			output.append("<del>%s</del>" % _html_transform(seq.a[a0:a1]))
		elif opcode == "replace":
			output.append("<del>%s</del><ins>%s</ins>" %
				(_html_transform(seq.a[a0:a1]), _html_transform(seq.b[b0:b1])))
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


def _generate_response(content, environ, start_response):
	serialize_type, mime_type = web.get_serialize_type(environ) # XXX: not suitable here!?
	cache_header = ("Cache-Control", "no-cache") # ensure accessing latest HEAD revision
	content_header = ("Content-Type", mime_type) # XXX: should be determined by diff format
	response = [cache_header, content_header]
	start_response("200 OK", response)
	return [content]


def _html_transform(str):
	"""
	escape a string to be HTML-safe

	also replaces line breaks with BR elements in order to make them visible
	"""
	return cgi.escape(str).replace("\n", " <br />\n")
