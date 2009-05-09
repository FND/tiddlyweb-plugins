"""
Flickr Store
TiddlyWeb StorageInterface interfacing with Flickr

Tiddler Mapping:
* bag ~ user
* title ~ ID
* created ~ date uploaded
* tags ~ tags
* text ~ description
* fields.label ~ title
* fields.source ~ URI
* fields.license ~ license

To Do:
* cache tiddlers when generating bag
"""

import urllib2
import logging

import simplejson

from tiddlyweb.stores import StorageInterface
from tiddlyweb.model.tiddler import Tiddler


class Store(StorageInterface):

	def __init__(self, environ=None):
		super(Store, self).__init__(environ)

	def list_bags(self):
		logging.debug("listing bag: %s" % bag.name)
		raise NotImplementedError("list of bags not available") # TODO?

	def list_tiddlers(self):
		logging.debug("listing bag: %s" % bag.name)
		raise NotImplementedError("list of bags not available") # TODO?

	def bag_get(self, bag):
		logging.debug("retrieving bag: %s" % bag.name)

		bag.desc = None # TODO
		#bag.policy = None # TODO

		if not (hasattr(bag, "skinny") and bag.skinny):
			for photo in _get_photos(bag.name):
				tiddler = Tiddler(photo["id"])
				tiddler = _populate_tiddler(tiddler)
				bag.add_tiddler(tiddler)

		return bag

	def tiddler_get(self, tiddler):
		logging.debug("retrieving tiddler %s from %s" % (tiddler.title, tiddler.bag))
		tiddler = _populate_tiddler(tiddler)
		return tiddler


def _get_photos(user_id):
	uri_template = "http://query.yahooapis.com/v1/public/yql?q=SELECT%20id%20FROM%20flickr.photos.search%20WHERE%20user_id%3D%22%s%22%20AND%20ispublic%3D%221%22&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
	uri = uri_template.replace("%s", urllib2.quote(user_id)) # N.B.: regular string substitution does not work well with URL-encoded strings
	data = urllib2.urlopen(uri)
	data = simplejson.loads(data.read())
	return data["query"]["results"]["photo"]


def _get_photo(id):
	uri_template = "http://query.yahooapis.com/v1/public/yql?q=SELECT%20title%2C%20dateuploaded%2C%20description%2C%20tags%2C%20license%20FROM%20flickr.photos.info%20WHERE%20photo_id%3D%22%s%22&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env"
	uri = uri_template.replace("%s", urllib2.quote(id)) # N.B.: regular string substitution does not work well with URL-encoded strings
	data = urllib2.urlopen(uri)
	data = simplejson.loads(data.read())
	photo = data["query"]["results"]["photo"]
	 # TODO: convert dateuploaded to date object, resolve license, store source URI
	tags = []
	try:
		for tag in photo["tags"]["tag"]:
			tags.append(tag["content"])
	except TypeError: # XXX: not quite sure why this fails sometimes
		pass
	photo["tags"] = tags
	return photo


def _populate_tiddler(tiddler):
	photo = _get_photo(tiddler.title)
	tiddler.created = photo["dateuploaded"] # TODO: convert to tiddly timestamp
	tiddler.text = photo["description"]
	tiddler.tags = photo["tags"]
	tiddler.fields["label"] = photo["title"]
	tiddler.fields["license"] = photo["license"]
	return tiddler
