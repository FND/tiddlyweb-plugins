"""
utility module for retrieving TiddlerS from Cook-style TiddlyWiki resources

supports .tiddler, .tid, .js and .recipe files
"""

# TODO: rename from_* functions to get_tiddler(s)_from_*?

import os

from urllib2 import urlopen, unquote, URLError, HTTPError

from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.serializer import Serializer
from tiddlyweb.util import read_utf8_file


def from_list(uris):
	"""
	generates collection of TiddlerS from a list of URIs

	supports .tiddler, .tid, .js and .recipe files
	"""
	sources = []
	for uri in uris:
		if uri.endswith(".recipe"):
			urls = _expand_recipe(uri)
			sources.extend(urls)
		else:
			sources.append(uri)

	return [from_source(uri) for uri in sources]


#def from_recipe(uri): # TODO?


def from_source(uri):
	"""
	generates Tiddler from the given resource

	supports .tiddler, .tid and .js files
	"""
	if uri.endswith(".js"):
		return from_plugin(uri)
	elif uri.endswith(".tid"):
		return from_tid(uri)
	else:
		return from_tiddler(uri)


def from_plugin(uri):
	"""
	generates Tiddler from a JavaScript (and accompanying meta) file

	If there is no .meta file, title and tags assume default values.
	"""
	default_title = _get_title_from_uri(uri, ".js")
	default_tags = "systemConfig"

	meta_uri = "%s.meta" % uri
	try:
		meta_content = _get_uri(meta_uri)
	except (HTTPError, URLError):
		meta_content = "title: %s\ntags: %s\n" % (default_title, default_tags)

	try:
		title = [line for line in meta_content.split("\n")
			if line.startswith("title:")][0]
		title = title.split(":", 1)[1].strip()
	except IndexError:
		title = default_title
	tiddler_meta = "\n".join(line for line in meta_content.split("\n")
		if not line.startswith("title:")).rstrip()

	plugin_content = _get_uri(uri)
	tiddler_text = "%s\n\n%s" % (tiddler_meta, plugin_content)

	return _from_text(title, tiddler_text)


def from_tid(uri):
	"""
	generates Tiddler from a TiddlyWeb-style .tid file
	"""
	title = _get_title_from_uri(uri, ".tid")
	content = _get_uri(uri)
	return _from_text(title, content)


def from_tiddler(uri):
	"""
	generates Tiddler from a Cook-style .tiddler file
	"""
	from html5lib import HTMLParser, treebuilders
	from tiddlywebwiki.tiddlywiki import get_tiddler_from_div

	content = _get_uri(uri)

	parser = HTMLParser(tree=treebuilders.getTreeBuilder("beautifulsoup"))
	content = _escape_brackets(content)
	doc = parser.parse(content)
	node = doc.find("div")

	return get_tiddler_from_div(node)


def _expand_recipe(uri): # XXX: adapted from devstore
	"""
	returns list of tiddler references specified in a Cook-style recipe

	supports recursive references to other recipes
	"""
	base_dir = os.path.dirname(uri)

	lines = _get_uri(uri).splitlines()
	rules = [line.rstrip() for line in lines if
		line.startswith("tiddler:") or
		line.startswith("plugin:") or
		line.startswith("recipe:")]

	uris = []
	for rule in rules:
		type, uri = rule.split(": ")
		uri = os.path.join(base_dir, uri)
		if type == "recipe":
			uris = uris + _expand_recipe(uri)
		else:
			uris.append(uri)

	return uris


def _from_text(title, content):
	"""
	generates Tiddler from an RFC822-style string

	This corresponds to TiddlyWeb's text serialization of TiddlerS.
	"""
	tiddler = Tiddler(title)
	serializer = Serializer("text")
	serializer.object = tiddler
	serializer.from_string(content)
	return tiddler


def _escape_brackets(content): # safeguard against broken .tiddler files -- XXX: obsolete?
	"""
	escapes angle brackets in tiddler's HTML representation
	"""
	open_pre = content.index("<pre>")
	close_pre = content.rindex("</pre>")
	start = content[0:open_pre+5]
	middle = content[open_pre+5:close_pre]
	end = content[close_pre:]
	middle = middle.replace(">", "&gt;").replace("<", "&lt;")
	return start + middle + end


def _get_title_from_uri(uri, extension):
	title = uri.split("/")[-1]
	title = _strip_extension(title, extension)
	title = unquote(title)
	if not type(title) == unicode:
		title = unicode(title, "utf-8")
	return title


def _strip_extension(name, ext):
	"""
	removes trailing extension from name
	"""
	ext_len = len(ext)
	if name[-ext_len:] == ext:
		name = name[:-ext_len]
	return name


def _get_uri(uri):
	try:
		content = urlopen(uri).read()
		content = unicode(content, "utf-8")
	except ValueError:
		content = read_utf8_file(uri)
	return content.replace("\r", "")
