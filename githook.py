"""
GitHook
turns commits into tiddlers using GitHub's post-receive hooks
includes a renderer for displaying commit tiddlers

Usage:
  POST /commit

Accepts JSON format described here:
    http://github.com/guides/post-receive-hooks

TODO:
* convert timestamps to tiddler date strings
* configurable bag name
* tests
"""

import simplejson as json

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web import util as web


__version__ = "0.2.0"

content_type = "text/x-commit"


def init(config):
	config["selector"].add("/commit", POST=post_request)
	# register renderer
	config["wikitext.type_render_map"][content_type] = __name__


def post_request(environ, start_response):
	length = int(environ["CONTENT_LENGTH"])
	data = environ["wsgi.input"].read(length).decode("utf-8") # XXX: simplejson takes care of decoding!?
	data = json.loads(data) # XXX: use load, not loads?

	store = environ["tiddlyweb.store"]
	for commit in data["commits"]:
		tiddler = _create_tiddler(commit)
		store.put(tiddler)

	start_response("204 No Content", []) # XXX: appropriate?
	return []


def render(tiddler, environ):
	"""
	render a commit tiddler as HTML
	"""
	template = "<pre>%s\n\n%s\n\n%s</pre>"
	files = "\n".join(
		_list_file_changes(tiddler, "added", "+") +
		_list_file_changes(tiddler, "removed", "-") +
		_list_file_changes(tiddler, "modified", "*"))
	return template % (tiddler.fields["uri"], files, tiddler.text)


def _create_tiddler(commit):
	tiddler = Tiddler(commit["id"])
	tiddler.bag = "commits" # XXX: hardcoded
	#tiddler.created = commit["timestamp"] # XXX: convert timestamp
	#tiddler.modified = tiddler.created # XXX: use time of notification?
	tiddler.modifier = commit["author"]["name"]
	tiddler.type = content_type
	tiddler.fields = {
		"uri": commit["url"],
		"files_added": _get_file_changes(commit, "added"),
		"files_removed": _get_file_changes(commit, "removed"),
		"files_modified": _get_file_changes(commit, "modified")
	}
	tiddler.text = commit["message"]
	return tiddler


def _get_file_changes(commit, type):
	items = commit.get(type, [])
	return json.dumps(items)


def _list_file_changes(tiddler, type, prefix):
	files = json.loads(tiddler.fields["files_%s" % type])
	return ["%s %s" % (prefix, filename) for filename in files]
