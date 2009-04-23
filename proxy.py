"""
TiddlyWeb plugin for proxying access to remote web pages

This is usually required to get around same-origin policy restrictions, e.g.
when importing TiddlyWiki documents.

Usage:
  GET /proxy/<URL>

To Do:
* character-encoding handling
* content-type handling
* whitelist support
"""

from urllib2 import urlopen

from tiddlyweb.web import util as web
from tiddlyweb.web.http import HTTP400


__version__ = "0.1.0"


def init(config):
	# extend urls.map
	config["selector"].add("/proxy/{url:any}", GET=get_request)


def get_request(environ, start_response):
	url = environ["selector.vars"]["url"]
	if not "://" in url:
		url = "http://%s" % url # XXX: magic!?
	req = urlopen(url)
	if req.code == 200:
		return _generate_response(req, environ, start_response)
	else:
		raise HTTP400("error loading %s: %s" % (url, req.msg)) # XXX: 400 not appropriate?


def _generate_response(content, environ, start_response):
	serialize_type, mime_type = web.get_serialize_type(environ)
	content_header = ("Content-Type", mime_type) # XXX: not correct!?
	response = [content_header]
	start_response("200 OK", response)
	return content # N.B.: must be an iterator
