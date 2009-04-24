"""
TiddlyWeb plugin for proxying access to remote web pages

This is usually required to get around same-origin policy restrictions, e.g.
when importing TiddlyWiki documents.

Usage:
  GET /proxy/<URL>

Configuration:
The TiddlyWeb configuration should be extended with a list of permitted host
names (domains) using the "proxy_whitelist" key.
Example:
	config = {
		"system_plugins": ["proxy"],
		"proxy_whitelist": ["tiddlyspot.com"]
	}

To Do:
* tests
"""

from urllib2 import urlopen
from urlparse import urlparse

from tiddlyweb.web import util as web
from tiddlyweb.web.http import HTTP400

from tiddlywebplugins import require_any_user


__version__ = "0.3.1"

whitelist = []


def init(config):
	# extend urls.map
	config["selector"].add("/proxy/{url:any}", GET=get_request)


@require_any_user()
def get_request(environ, start_response):
	url = environ["wsgiorg.routing_args"][1]["url"]
	if not "://" in url:
		url = "http://%s" % url # XXX: magic!?

	whitelist = environ["tiddlyweb.config"]["proxy_whitelist"]
	if _whitelisted(url, whitelist):
		req = urlopen(url)
	else:
		raise HTTP400("error loading %s: unautorized" % url) # XXX: 400 not appropriate?

	content_type = req.info()["Content-Type"]
	try:
		content_type, charset = content_type.split("; charset=")
	except ValueError: # charset not specified
		charset = "UTF-8" # XXX: use lowercase?
	mime_type = "%s; %s" % (content_type, charset)

	if req.code == 200:
		return _generate_response(req, mime_type, environ, start_response)
	else:
		raise HTTP400("error loading %s: %s" % (url, req.msg)) # XXX: 400 not appropriate?


def _whitelisted(url, items):
	host = urlparse(url).hostname
	for item in items:
		if host.endswith(item): # XXX: insecure?
			return True
	return False


def _generate_response(content, mime_type, environ, start_response):
	content_header = ("Content-Type", mime_type) # XXX: not correct!?
	response = [content_header]
	start_response("200 OK", response)
	return content # N.B.: must be an iterator
