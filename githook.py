"""
GitHook
turns commits into tiddlers using GitHub's post-receive hooks

Usage:
  POST /commit

Accepts JSON format described here:
    http://github.com/guides/post-receive-hooks

TODO:
* use custom fields instead of dumping data in tiddler.text
* tests
"""

from simplejson import loads as json # XXX: use load, not loads?

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.web import util as web


__version__ = "0.1.0"


def init(config):
	config["selector"].add("/commit", POST=post_request)


def post_request(environ, start_response):
	length = int(environ["CONTENT_LENGTH"])
	data = environ["wsgi.input"].read(length).decode("utf-8") # XXX: simplejson takes care of decoding!?
	data = json(data)

	store = environ["tiddlyweb.store"]
	for commit in data["commits"]:
		tiddler = _create_tiddler(commit)
		store.put(tiddler)

	start_response("204 No Content", []) # XXX: appropriate?
	return []


def _create_tiddler(commit):
	files = "\n".join(
		_list_changes(commit, "added", "+") +
		_list_changes(commit, "removed", "-") +
		_list_changes(commit, "modified", "*"))

	tiddler = Tiddler(commit["id"])
	tiddler.bag = "commits" # XXX: hardcoded
	tiddler.created = commit["timestamp"] # XXX: convert timestamp
	tiddler.modified = tiddler.created # XXX: use time of notification?
	tiddler.modifier = commit["author"]["name"]
	tiddler.text = "%s\n\n%s\n\n%s" % (commit["url"], files, commit["message"])

	return tiddler


def _list_changes(commit, type, prefix):
	return ["%s %s" % (prefix, filename) for filename in commit.get(type, [])]
